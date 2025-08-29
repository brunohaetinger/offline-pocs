#!/usr/bin/env python3
"""
Simple curses-based system monitor.
Requirements: psutil (pip install psutil)
GPU: will try to query `nvidia-smi` if available; otherwise shows N/A.
"""
import curses
import psutil
import shutil
import subprocess
import time
from datetime import datetime

REFRESH = 1.0  # seconds

def get_gpu_info():
    """Try nvidia-smi for a compact GPU status. Return string."""
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.total,memory.used,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=1
        )
        if p.returncode == 0 and p.stdout.strip():
            lines = [ln.strip() for ln in p.stdout.strip().splitlines()]
            # Format first GPU summary (if multiple GPUs, join them)
            parts = []
            for ln in lines:
                # name, util, mem_total, mem_used, temp
                cols = [c.strip() for c in ln.split(",")]
                if len(cols) >= 5:
                    name, util, mem_tot, mem_used, temp = cols[:5]
                    parts.append(f"{name} {util}% {mem_used}/{mem_tot}MiB {temp}°C")
                else:
                    parts.append(ln)
            return " | ".join(parts)
    except Exception:
        pass
    return "N/A"

def human_bytes(n):
    # simple human readable transformation
    for unit in ["B","KiB","MiB","GiB","TiB"]:
        if abs(n) < 1024.0:
            return f"{n:3.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PiB"

def draw_progress(stdscr, y, x, width, percent, label=""):
    """Draw a horizontal progress bar at (y,x) width cells (including brackets)"""
    if width < 6:
        return
    inner = width - 2
    filled = int(inner * percent / 100.0)
    bar = "[" + ("#" * filled).ljust(inner) + "]"
    try:
        stdscr.addstr(y, x, bar)
        if label:
            stdscr.addstr(y, x + width + 1, label)
    except curses.error:
        pass

def render(stdscr, show_per_core=False):
    h, w = stdscr.getmaxyx()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stdscr.addstr(0, 0, f"Resources app — {now}".ljust(w-1), curses.A_REVERSE)

    # CPU summary
    cpu_pct = psutil.cpu_percent(interval=None)
    load1, load5, load15 = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0.0,0.0,0.0)
    stdscr.addstr(2, 0, f"CPU: {cpu_pct:5.1f}%   Load: {load1:.2f} {load5:.2f} {load15:.2f}")
    draw_progress(stdscr, 3, 0, min(40, w-2), cpu_pct, "")

    # Per-core
    if show_per_core:
        cores = psutil.cpu_percent(interval=None, percpu=True)
        for i, c in enumerate(cores):
            y = 5 + i
            if y >= h-3: break
            label = f"cpu{i:02d}:{c:5.1f}%"
            draw_progress(stdscr, y, 0, min(36, w-2), c, label)

    # Memory
    vm = psutil.virtual_memory()
    mem_line = f"Mem: {human_bytes(vm.used)}/{human_bytes(vm.total)} ({vm.percent}%)"
    y = 5 + (len(psutil.cpu_percent(percpu=True)) if show_per_core else 0)
    if y+6 >= h:
        y = max(6, h-8)
    stdscr.addstr(y, 0, mem_line)
    draw_progress(stdscr, y+1, 0, min(40, w-2), vm.percent, "")

    # Swap
    sw = psutil.swap_memory()
    sw_line = f"Swap: {human_bytes(sw.used)}/{human_bytes(sw.total)} ({sw.percent}%)"
    stdscr.addstr(y+3, 0, sw_line)
    draw_progress(stdscr, y+4, 0, min(40, w-2), sw.percent, "")

    # Disk (root)
    try:
        du = psutil.disk_usage("/")
        disk_line = f"Disk(/): {human_bytes(du.used)}/{human_bytes(du.total)} ({du.percent}%)"
        stdscr.addstr(y, 45, disk_line)
        draw_progress(stdscr, y+1, 45, min(40, w-45-2), du.percent, "")
    except Exception:
        stdscr.addstr(y, 45, "Disk: N/A")

    # Disk partitions summary (small)
    try:
        # show top 3 by percent
        parts = psutil.disk_partitions(all=False)
        dlist = []
        for p in parts:
            try:
                st = psutil.disk_usage(p.mountpoint)
                dlist.append((st.percent, p.mountpoint))
            except Exception:
                continue
        dlist.sort(reverse=True)
        for i, (pct, m) in enumerate(dlist[:3]):
            stdscr.addstr(y+3+i, 45, f"{m} {pct}%")
    except Exception:
        pass

    # Battery
    try:
        batt = psutil.sensors_battery()
        if batt is not None:
            batt_pct = batt.percent
            plugged = batt.power_plugged
            bstatus = "Charging" if plugged else "Discharging"
            stdscr.addstr(y+7, 0, f"Battery: {batt_pct:.0f}% ({bstatus})")
            draw_progress(stdscr, y+8, 0, min(40, w-2), batt_pct, "")
        else:
            stdscr.addstr(y+7, 0, "Battery: N/A")
    except Exception:
        stdscr.addstr(y+7, 0, "Battery: N/A")

    # GPU
    gpu = get_gpu_info()
    stdscr.addstr(y+3, 0, f"GPU: {gpu}")

    # Footer help
    footer = "q:quit  p:pause  c:toggle cores  r:refresh"
    try:
        stdscr.addstr(h-1, 0, footer.ljust(w-1), curses.A_REVERSE)
    except curses.error:
        pass

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)  # non-blocking getch
    show_per_core = False
    paused = False
    last = 0.0

    # initial call to populate cpu_percent baseline
    psutil.cpu_percent(interval=None)
    while True:
        now = time.time()
        ch = stdscr.getch()
        if ch != -1:
            if ch in (ord('q'), 27):
                break
            elif ch == ord('p'):
                paused = not paused
            elif ch == ord('c'):
                show_per_core = not show_per_core
            elif ch == ord('r'):
                # immediate refresh
                pass

        if not paused and now - last >= REFRESH:
            stdscr.erase()
            render(stdscr, show_per_core=show_per_core)
            stdscr.refresh()
            last = now
        else:
            # small sleep to reduce CPU
            time.sleep(0.05)

if __name__ == "__main__":
    import sys
    try:
        curses.wrapper(main)
    except Exception as e:
        print("Error running curses app:", e)
        sys.exit(1)

