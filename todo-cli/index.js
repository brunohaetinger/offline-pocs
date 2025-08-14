const { Command } = require('commander');
const fs = require('fs');
const path = require('path');


const todoFile = path.join(__dirname, 'todos.json');

const program = new Command();

if(!fs.existsSync(todoFile)) {
  fs.writeFileSync(todoFile, JSON.stringify([]));
}

function loadTodos(){
  return JSON.parse(fs.readFileSync(todoFile , 'utf8'));
}

function saveTodos(todos) {
  fs.writeFileSync(todoFile, JSON.stringify(todos, null, 2));
}

let todos = [];

program
  .name('todo-cli')
  .description('To Do list in CLI')
  .version('0.8.0');

program.command('add <title>')
  .description('Add new to-do item')
  .action((itemTitle, options) => {
    todos = loadTodos();
    todos.push({ title: itemTitle, done: false});
    saveTodos(todos)
    console.log(`✅ Added: ${itemTitle}`)
  });

program.command('rm <id>')
  .description('Remove to-do item')
  .action((id, options) => {
    todos = loadTodos();
    todos = todos.filter(t => t.id == id);
    saveTodos(todos)
    console.log(`Removed item ${id}`);
  });

program.command('done <id>')
  .description('Complete to-do item')
  .action((id, options) => {
    todos = loadTodos();
    todos = todos.map(todo => todo.id === id ? {...todo, done: true} : todo);
    saveTodos(todos)
    console.log(`Removed item ${id}`);
  });


program.command('list')
  .description('List to-do items')
  .action((options) => {
    todos = loadTodos();
    console.table(todos)
  });

program.parse();
