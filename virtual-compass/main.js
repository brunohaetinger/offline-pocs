<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Browse Virtual Compass</title>
    <style>
        body {
            margin: 0;
            padding: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        
        canvas {
            border: 2px solid transparent;
        }
        
        .show-text { 
            color: white;
            padding: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="show-text">Directions:</div>
    
    <script src="https://unpkg.com/directionapi@latest/dist/index.js"></script>
    
    <script>
        let deviceOrientation = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize horizontal tilt level
            deviceOrientation.init_horizontal_position();
            
            // Get orientation data
            const doa = deviceOrientation.get_horizontal_acceleration_level();
            
            // Calculate compass bearing
            let direction;
            if (doa['horizontal'] >= 100) {
                direction = "N";
            } else if (doa['horizontal'] >= 50 && doa['vertical'] < 20) {
                direction = "E";
            } else if (doa['horizontal'] >= -100) {
                direction = "S";
            } else if (doa['vertical'] < 30) {
                direction = "W";
            }
            
            // Draw compass needle
            const angle = (direction === 'N') * 90 + 
                         (direction === 'E') * 60 + 
                         (direction === 'S') * (-90) + 
                         (direction === 'W') * (-150);
            
            let canvasElement;
            document.getElementById('canvas').innerHTML = `
                <div style="width: 200px; height: 200px; border-radius: 5px; origin-left: 50%;">
                    ${angle}N
                    <canvas id="canvas" width={canvasElement.width} height={canvasElement.height}</canvas>
                </div>
            `;
        });
    </script>
</body>
</html>

