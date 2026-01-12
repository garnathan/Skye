import json
import os

def get_content():
    """Return the HTML content for the todo page"""
    
    html_content = '''
        <div class="todo-page">
            <h2><i class="fas fa-check-square"></i> To-Do List</h2>
            
            <div class="todo-input">
                <input type="text" id="todoInput" placeholder="Add a new task..." maxlength="200">
                <button id="addBtn"><i class="fas fa-plus"></i> Add</button>
            </div>
            
            <div id="todoList" class="todo-list">
                <!-- Tasks will be loaded here -->
            </div>
            
            <div class="notes-section">
                <h3><i class="fas fa-sticky-note"></i> Notes</h3>
                <textarea id="notesArea" placeholder="Add your notes here..."></textarea>
            </div>
        </div>
        
        <style>
        .todo-input {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .todo-input input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            color: #333;
        }
        
        .todo-input input::placeholder {
            color: #6c757d;
        }
        
        .todo-input button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .todo-list {
            margin-top: 1rem;
        }
        
        .todo-item {
            display: flex;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 0.75rem;
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #f8f9fa;
            border-radius: 8px;
            border: 2px solid #dee2e6;
        }
        
        .todo-item.completed {
            opacity: 0.6;
            text-decoration: line-through;
        }
        
        .todo-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .todo-text {
            flex: 1;
            font-size: 1rem;
            color: #333;
        }
        
        .todo-info {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            margin-right: 0.5rem;
        }
        
        .todo-info .has-notes {
            color: #ffd700;
        }
        
        .todo-delete {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        .todo-notes {
            display: none;
            margin-top: 0.5rem;
            width: 100%;
        }
        
        .todo-notes.show {
            display: block;
        }
        
        .todo-notes textarea {
            width: 100%;
            min-height: 60px;
            padding: 0.5rem;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 0.9rem;
            resize: vertical;
            background: white;
            color: #333;
        }
        
        .todo-notes textarea::placeholder {
            color: #6c757d;
        }
        
        .notes-section {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid #dee2e6;
        }
        
        .notes-section h3 {
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        #notesArea {
            width: 100%;
            min-height: 150px;
            padding: 0.75rem;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            resize: vertical;
            background: white;
            color: #333;
        }
        
        #notesArea::placeholder {
            color: #6c757d;
        }
        </style>
    '''
    
    js_code = '''
        <script>
        let todos = [];
        
        function loadTodos() {
            const saved = localStorage.getItem('skyeTodos');
            todos = saved ? JSON.parse(saved) : [];
            renderTodos();
        }
        
        function loadNotes() {
            const saved = localStorage.getItem('skyeNotes');
            const notesArea = document.getElementById('notesArea');
            if (notesArea && saved) {
                notesArea.value = saved;
            }
        }
        
        function saveNotes() {
            const notesArea = document.getElementById('notesArea');
            if (notesArea) {
                localStorage.setItem('skyeNotes', notesArea.value);
            }
        }
        
        function saveTodos() {
            localStorage.setItem('skyeTodos', JSON.stringify(todos));
        }
        
        function renderTodos() {
            const list = document.getElementById('todoList');
            if (!list) return;
            
            list.innerHTML = todos.map((todo, index) => `
                <div class="todo-item ${todo.completed ? 'completed' : ''}">
                    <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''} 
                           onchange="toggleTodo(${index})">
                    <span class="todo-text">${todo.text}</span>
                    <button class="todo-info" onclick="toggleNotes(${index})" title="Add notes">
                        <i class="fas fa-info-circle ${todo.notes ? 'has-notes' : ''}"></i>
                    </button>
                    <button class="todo-delete" onclick="deleteTodo(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                    <div class="todo-notes ${todo.showNotes ? 'show' : ''}">
                        <textarea placeholder="Add notes for this task..." 
                                  onchange="updateNotes(${index}, this.value)">${todo.notes || ''}</textarea>
                    </div>
                </div>
            `).join('');
        }
        
        function addTodo() {
            const input = document.getElementById('todoInput');
            const text = input.value.trim();
            if (text) {
                todos.push({ text, completed: false, notes: '' });
                input.value = '';
                saveTodos();
                renderTodos();
            }
        }
        
        function toggleTodo(index) {
            todos[index].completed = !todos[index].completed;
            saveTodos();
            renderTodos();
        }
        
        function deleteTodo(index) {
            todos.splice(index, 1);
            saveTodos();
            renderTodos();
        }
        
        function toggleNotes(index) {
            todos[index].showNotes = !todos[index].showNotes;
            renderTodos();
        }
        
        function updateNotes(index, value) {
            todos[index].notes = value;
            saveTodos();
            renderTodos();
        }
        
        setTimeout(function() {
            loadTodos();
            loadNotes();
            
            const addBtn = document.getElementById('addBtn');
            const input = document.getElementById('todoInput');
            const notesArea = document.getElementById('notesArea');
            
            if (addBtn) addBtn.addEventListener('click', addTodo);
            if (input) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') addTodo();
                });
            }
            if (notesArea) {
                notesArea.addEventListener('input', saveNotes);
            }
        }, 100);
        </script>
    '''
    
    return {
        'html': html_content + js_code
    }