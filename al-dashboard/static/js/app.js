// Al Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadTasks();
    loadWorkers();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadStats();
        loadTasks();
    }, 30000);
});

// Chat Form
const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-message');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';
    
    // Send to API
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response, 'al');
        } else {
            addMessage('Error: ' + data.error, 'system');
        }
    } catch (error) {
        addMessage('Connection error: ' + error.message, 'system');
    }
});

function addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Load Stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('total-tasks').textContent = data.stats.total;
            document.getElementById('todo-tasks').textContent = data.stats.todo;
            document.getElementById('progress-tasks').textContent = data.stats.in_progress;
            document.getElementById('done-tasks').textContent = data.stats.done;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load Tasks
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        if (data.success) {
            renderKanban(data.tasks);
        }
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

function renderKanban(tasks) {
    const todoColumn = document.getElementById('todo-column');
    const progressColumn = document.getElementById('progress-column');
    const doneColumn = document.getElementById('done-column');
    
    todoColumn.innerHTML = '';
    progressColumn.innerHTML = '';
    doneColumn.innerHTML = '';
    
    tasks.forEach(task => {
        const card = createTaskCard(task);
        
        if (task.status === 'todo') {
            todoColumn.appendChild(card);
        } else if (task.status === 'in_progress') {
            progressColumn.appendChild(card);
        } else if (task.status === 'done') {
            doneColumn.appendChild(card);
        }
    });
}

function createTaskCard(task) {
    const div = document.createElement('div');
    div.className = 'task-card';
    div.innerHTML = `
        <h4>${task.title}</h4>
        <span class="assignee">${task.assignee || 'Unassigned'}</span>
    `;
    return div;
}

// Load Workers
async function loadWorkers() {
    try {
        const response = await fetch('/api/workers');
        const data = await response.json();
        
        if (data.success) {
            renderWorkers(data.workers);
        }
    } catch (error) {
        console.error('Failed to load workers:', error);
    }
}

function renderWorkers(workers) {
    const list = document.getElementById('worker-list');
    list.innerHTML = '';
    
    workers.forEach(worker => {
        const card = document.createElement('div');
        card.className = 'worker-card';
        card.innerHTML = `
            <div class="worker-info">
                <div class="worker-avatar">${worker.name[0]}</div>
                <div class="worker-details">
                    <h4>${worker.name}</h4>
                    <p>${worker.role}</p>
                </div>
            </div>
            <span class="worker-status ${worker.status}">${worker.status}</span>
        `;
        list.appendChild(card);
    });
}
