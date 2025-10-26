// Data model and persistence for Colorful Todo app

class Task {
  constructor(id, text, dueDate = null, completed = false) {
    this.id = id;
    this.text = text;
    this.dueDate = dueDate;
    this.completed = completed;
  }
}

// Global task list
let tasks = [];

// Save tasks to localStorage
function saveTasks() {
  try {
    const serialized = JSON.stringify(tasks);
    localStorage.setItem('colorfulTodoTasks', serialized);
  } catch (e) {
    console.error('Failed to save tasks:', e);
  }
}

// Load tasks from localStorage
function loadTasks() {
  const data = localStorage.getItem('colorfulTodoTasks');
  if (!data) {
    tasks = [];
    return;
  }
  try {
    const parsed = JSON.parse(data);
    // Recreate Task instances
    tasks = parsed.map(item => new Task(item.id, item.text, item.dueDate, item.completed));
  } catch (e) {
    console.error('Failed to load tasks:', e);
    tasks = [];
  }
}

/**
 * Create a DOM element representing a single task.
 * @param {Task} task
 * @returns {HTMLLIElement}
 */
function createTaskElement(task) {
  const li = document.createElement('li');
  li.className = 'task-item';
  li.dataset.id = task.id;
+
+  // Enable drag-and-drop reordering
+  li.setAttribute('draggable', 'true');
+
+  // Drag start – store the dragged task ID and add visual cue
+  li.addEventListener('dragstart', (e) => {
+    e.dataTransfer.setData('text/plain', task.id.toString());
+    li.classList.add('dragging');
+  });
+
+  // Drag over – allow drop by preventing default behavior
+  li.addEventListener('dragover', (e) => {
+    e.preventDefault();
+  });
+
+  // Drop – reorder tasks array based on source and target IDs
+  li.addEventListener('drop', (e) => {
+    e.preventDefault();
+    const draggedId = Number(e.dataTransfer.getData('text/plain'));
+    const targetId = Number(li.dataset.id);
+    if (draggedId === targetId) return; // No change needed
+
+    const draggedIdx = tasks.findIndex(t => t.id === draggedId);
+    const targetIdx = tasks.findIndex(t => t.id === targetId);
+    if (draggedIdx === -1 || targetIdx === -1) return;
+
+    // Remove the dragged task
+    const [movedTask] = tasks.splice(draggedIdx, 1);
+    // Determine insertion index (adjust if original index was before target)
+    let insertIdx = targetIdx;
+    if (draggedIdx < targetIdx) insertIdx = targetIdx - 1;
+    tasks.splice(insertIdx, 0, movedTask);
+
+    saveTasks();
+    renderTaskList(currentFilter);
+  });
+
+  // Drag end – clean up visual cue
+  li.addEventListener('dragend', () => {
+    li.classList.remove('dragging');
+  });

  // Completion checkbox
  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.checked = task.completed;
  checkbox.className = 'task-checkbox';
  li.appendChild(checkbox);

  // Editable task text
  const textSpan = document.createElement('span');
  textSpan.className = 'task-text';
  textSpan.contentEditable = true;
  textSpan.textContent = task.text;
  li.appendChild(textSpan);

  // Optional due date
  if (task.dueDate) {
    const dueSpan = document.createElement('span');
    dueSpan.className = 'task-due';
    dueSpan.textContent = task.dueDate;
    li.appendChild(dueSpan);
  }

  // Edit button (focuses the text span)
  const editBtn = document.createElement('button');
  editBtn.className = 'edit-btn';
  editBtn.textContent = 'Edit';
  li.appendChild(editBtn);

  // Delete button
  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.textContent = 'Delete';
  li.appendChild(deleteBtn);

  // Apply completed styling if needed
  if (task.completed) {
    li.classList.add('completed');
  }

  // Event: toggle completion
  checkbox.addEventListener('change', handleToggleComplete);

  // Event: inline edit (on blur)
  textSpan.addEventListener('blur', handleEditTask);

  // Prevent newline on Enter while editing
  textSpan.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      textSpan.blur();
    }
  });

  // Edit button – simply focus the editable span
  editBtn.addEventListener('click', () => {
    textSpan.focus();
  });

  // Delete button – remove from array and DOM
  deleteBtn.addEventListener('click', handleDeleteTask);

  return li;
}

/**
 * Render the task list according to the provided filter.
 * @param {string} filter - 'all', 'active', or 'completed'
 */
function renderTaskList(filter = 'all') {
  const listEl = document.getElementById('task-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true; // 'all'
  });

  filteredTasks.forEach(task => {
    const taskEl = createTaskElement(task);
    listEl.appendChild(taskEl);
  });
}

// Filter button handling (optional but useful)
let currentFilter = 'all';
function setFilter(filter) {
  currentFilter = filter;
  // Update active button styling
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.id === `filter-${filter}`);
  });
  renderTaskList(currentFilter);
}

// Attach click listeners to filter buttons
document.getElementById('filter-all')?.addEventListener('click', () => setFilter('all'));
document.getElementById('filter-active')?.addEventListener('click', () => setFilter('active'));
document.getElementById('filter-completed')?.addEventListener('click', () => setFilter('completed'));

/**
 * Handle form submission to add a new task.
 * @param {Event} event
 */
function handleAddTask(event) {
  event.preventDefault();
  const textInput = document.getElementById('new-task-input');
  const dueInput = document.getElementById('new-task-due');
  if (!textInput) return;
  const text = textInput.value.trim();
  if (!text) return; // ignore empty tasks
  const dueDate = dueInput && dueInput.value ? dueInput.value : null;
  const newTask = new Task(Date.now(), text, dueDate, false);
  tasks.push(newTask);
  saveTasks();
  renderTaskList(currentFilter);
  // Clear inputs
  textInput.value = '';
  if (dueInput) dueInput.value = '';
}

/**
 * Handle inline edit of a task's text.
 * @param {Event} event
 */
function handleEditTask(event) {
  const span = event.target;
  const li = span.closest('li');
  if (!li) return;
  const id = Number(li.dataset.id);
  const task = tasks.find(t => t.id === id);
  if (!task) return;
  const newText = span.textContent.trim();
  if (newText && newText !== task.text) {
    task.text = newText;
    saveTasks();
  }
}

/**
 * Handle deletion of a task.
 * @param {Event} event
 */
function handleDeleteTask(event) {
  const btn = event.target;
  const li = btn.closest('li');
  if (!li) return;
  const id = Number(li.dataset.id);
  const idx = tasks.findIndex(t => t.id === id);
  if (idx !== -1) {
    tasks.splice(idx, 1);
    saveTasks();
  }
  li.remove();
}

/**
 * Handle toggling a task's completed state.
 * @param {Event} event
 */
function handleToggleComplete(event) {
  const checkbox = event.target;
  const li = checkbox.closest('li');
  if (!li) return;
  const id = Number(li.dataset.id);
  const task = tasks.find(t => t.id === id);
  if (!task) return;
  task.completed = checkbox.checked;
  if (task.completed) {
    li.classList.add('completed');
  } else {
    li.classList.remove('completed');
  }
  saveTasks();
}

// Attach add task handler to form submission
document.getElementById('task-form')?.addEventListener('submit', handleAddTask);

// Initial load and render with default filter (sets active button styling)
loadTasks();
setFilter('all');

// Export to window for external access (optional)
window.Task = Task;
window.tasks = tasks;
window.saveTasks = saveTasks;
window.loadTasks = loadTasks;
window.createTaskElement = createTaskElement;
window.renderTaskList = renderTaskList;
