// Comments JavaScript functionality
let currentArticleId = null;

// Initialize comments functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get article ID from URL or page data
    const pathParts = window.location.pathname.split('/');
    if (pathParts[1] === 'article' && pathParts[2]) {
        currentArticleId = parseInt(pathParts[2]);
        loadComments();
    }
    
    // Set up category selection handler
    const categorySelect = document.getElementById('category-select');
    if (categorySelect) {
        categorySelect.addEventListener('change', handleCategorySelection);
    }
});

// Handle category selection dropdown
function handleCategorySelection() {
    const categorySelect = document.getElementById('category-select');
    const newCategoryGroup = document.getElementById('new-category-group');
    
    if (categorySelect.value === 'new') {
        newCategoryGroup.style.display = 'block';
    } else {
        newCategoryGroup.style.display = 'none';
    }
}

// Create new category
async function createNewCategory() {
    const nameInput = document.getElementById('new-category-name');
    const descriptionInput = document.getElementById('new-category-description');
    
    const categoryName = nameInput.value.trim();
    if (!categoryName) {
        alert('Please enter a category name');
        return;
    }
    
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: categoryName,
                description: descriptionInput.value.trim() || null
            })
        });
        
        if (response.ok) {
            const newCategory = await response.json();
            
            // Add to dropdown
            const categorySelect = document.getElementById('category-select');
            const newOption = document.createElement('option');
            newOption.value = newCategory.id;
            newOption.textContent = newCategory.name;
            categorySelect.insertBefore(newOption, categorySelect.lastElementChild);
            
            // Select the new category
            categorySelect.value = newCategory.id;
            
            // Hide the new category form
            document.getElementById('new-category-group').style.display = 'none';
            
            // Clear inputs
            nameInput.value = '';
            descriptionInput.value = '';
            
            alert('Category created successfully!');
        } else {
            const errorData = await response.json();
            alert('Error creating category: ' + (errorData.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error creating category:', error);
        alert('Error creating category. Please try again.');
    }
}

// Add comment function
async function addComment(event) {
    event.preventDefault();
    
    if (!currentArticleId) {
        alert('Unable to determine article ID');
        return;
    }
    
    const form = document.getElementById('comment-form');
    const formData = new FormData(form);
    
    const commentData = {
        comment_text: formData.get('comment_text'),
        user_name: formData.get('user_name') || null,
        category_id: formData.get('category_id') ? parseInt(formData.get('category_id')) : null
    };
    
    if (!commentData.comment_text.trim()) {
        alert('Please enter a comment');
        return;
    }
    
    try {
        const response = await fetch(`/api/comments?news_id=${currentArticleId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(commentData)
        });
        
        if (response.ok) {
            const newComment = await response.json();
            
            // Clear form
            form.reset();
            document.getElementById('new-category-group').style.display = 'none';
            
            // Reload comments
            loadComments();
            
            alert('Comment added successfully!');
        } else {
            const errorData = await response.json();
            alert('Error adding comment: ' + (errorData.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding comment:', error);
        alert('Error adding comment. Please try again.');
    }
}

// Load and display comments
async function loadComments() {
    if (!currentArticleId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/comments/${currentArticleId}`);
        
        if (response.ok) {
            const comments = await response.json();
            displayComments(comments);
        } else {
            console.error('Error loading comments:', response.status);
            displayComments([]);
        }
    } catch (error) {
        console.error('Error loading comments:', error);
        displayComments([]);
    }
}

// Display comments in the UI
function displayComments(comments) {
    const commentsHeader = document.getElementById('comments-header');
    const commentsList = document.getElementById('comments-list');
    
    if (!commentsList) {
        return;
    }
    
    // Update header
    if (commentsHeader) {
        commentsHeader.textContent = `Comments (${comments.length})`;
    }
    
    // Clear existing comments
    commentsList.innerHTML = '';
    
    if (comments.length === 0) {
        commentsList.innerHTML = `
            <div class="no-comments">
                <p>No comments yet. Be the first to comment on this article!</p>
            </div>
        `;
        return;
    }
    
    // Display each comment
    comments.forEach(comment => {
        const commentElement = createCommentElement(comment);
        commentsList.appendChild(commentElement);
    });
}

// Create HTML element for a single comment
function createCommentElement(comment) {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment-item';
    
    const createdAt = new Date(comment.created_at);
    const formattedDate = createdAt.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    commentDiv.innerHTML = `
        <div class="comment-header">
            <div class="comment-meta">
                <span class="comment-author">${comment.user_name || 'Anonymous'}</span>
                <span class="comment-date">${formattedDate}</span>
                ${comment.category_name ? `<span class="comment-category">${comment.category_name}</span>` : ''}
            </div>
        </div>
        <div class="comment-content">
            ${comment.comment_text.replace(/\n/g, '<br>')}
        </div>
    `;
    
    return commentDiv;
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString();
    }
} 