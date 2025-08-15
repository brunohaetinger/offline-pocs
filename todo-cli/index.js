const { Command } = require('commander');
const fs = require('fs');
const path = require('path');


const todoFile = path.join(__dirname, 'todos.json');

const program = new Command();

if (!fs.existsSync(todoFile)) {
  fs.writeFileSync(todoFile, JSON.stringify([]));
}

function loadTodos() {
  return JSON.parse(fs.readFileSync(todoFile, 'utf8'));
}

function saveTodos(todos) {
  fs.writeFileSync(todoFile, JSON.stringify(todos, null, 2));
}


program
  .name('todo-cli')
  .description('To Do list in CLI')
  .version('0.8.0');

program.command('add <title>')
  .description('Add new to-do item')
  .action((itemTitle, options) => {
    const todos = loadTodos();
    todos.push({ title: itemTitle, done: false });
    saveTodos(todos)
    console.log(`✅ Added: ${itemTitle}`)
  });

program.command('rm <index>')
  .description('Remove to-do item')
  .action((index, options) => {
    const todos = loadTodos();
    const filteredTodos = todos.filter((todo, i) => i !== Number(index));
    saveTodos(filteredTodos)
    console.log(`Removed item at ${index}`);
  });

program.command('done <index>')
  .description('Complete to-do item')
  .action((index, options) => {
    const todos = loadTodos();
    const newTodos = todos.map((todo, i) => i === Number(index) ? { ...todo, done: true } : todo);
    saveTodos(newTodos)
    console.log(`Marked item at index ${index} as done`);
  });


program.command('ls')
  .description('List to-do items')
  .action((options) => {
    const todos = loadTodos();
    console.table(todos)
  });

program.parse();
