const { Command } = require('commander');
const program = new Command();

let todos = [];

program
  .name('todo-cli')
  .description('To Do list in CLI')
  .version('0.8.0');

program.command('add')
  .description('Add new to do item')
  .argument('<string>', 'Item title')
  .action((itemTitle, options) => {
    todos.push(itemTitle);
    console.log({itemTitle, options})
  });

program.parse();
