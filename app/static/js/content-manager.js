/**
 * Content Manager JavaScript
 * Handles content scraping, translation toggles, and category management
 */

class ContentManager {
    constructor() {
        this.currentLanguage = 'zh';
        this.currentArticleId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeLanguageToggle();
        this.loadArticleFromURL();
    }

    bindEvents() {
        // Content scraping
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="scrape-content"]')) {
                e.preventDefault();
                this.handleScrapeContent(e.target);
            }
            
            if (e.target.matches('[data-action="generate-summary"]')) {
                e.preventDefault();
                this.handleGenerateSummary(e.target);
            }
            
            if (e.target.matches('[data-action="save-to-category"]')) {
                e.preventDefault();
                this.handleSaveToCategory(e.target);
            }
            
            if (e.target.matches('.lang-btn')) {
                e.preventDefault();
                this.handleLanguageToggle(e.target);
            }
            
            if (e.target.matches('.category-card')) {
                this.handleCategorySelect(e.target);
            }
        });

        // Real-time updates
        this.startStatusPolling();
    }

    loadArticleFromURL() {
        const pathParts = window.location.pathname.split('/');
        if (pathParts[1] === 'article' && pathParts[2]) {
            this.currentArticleId = parseInt(pathParts[2]);
            this.loadArticleDetails(this.currentArticleId);
        }
    }

    async loadArticleDetails(articleId) {
        try {
            const response = await fetch(`/api/articles/${articleId}`);
            if (response.ok) {
                const article = await response.json();
                this.updateArticleDisplay(article);
            }
        } catch (error) {
            console.error('Failed to load article details:', error);
            this.showMessage('Failed to load article details', 'error');
        }
    }

    updateArticleDisplay(article) {
        // Update title and meta information
        document.querySelector('.article-title').textContent = article.title;
        
        const englishTitle = document.querySelector('.article-title-english');
        if (englishTitle && article.title_english) {
            englishTitle.textContent = article.title_english;
        }

        // Update status badges
        this.updateStatusBadges(article);
        
        // Update content sections
        this.updateContentSections(article);
        
        // Update action buttons
        this.updateActionButtons(article);
    }

    updateStatusBadges(article) {
        const statusElements = {
            'content-status': article.is_content_scraped,
            'translation-status': article.is_content_translated,
            'summary-status': article.is_summarized
        };

        Object.entries(statusElements).forEach(([className, status]) => {
            const element = document.querySelector(`.${className}`);
            if (element) {
                element.className = `status-badge ${status ? 'status-scraped' : 'status-not-scraped'}`;
                element.textContent = status ? 'Complete' : 'Pending';
            }
        });
    }

    updateContentSections(article) {
        // Full content
        const contentSection = document.querySelector('#content-section');
        if (contentSection) {
            if (article.full_content || article.full_content_english) {
                contentSection.classList.remove('hidden');
                this.updateContentText('full-content-zh', article.full_content);
                this.updateContentText('full-content-en', article.full_content_english);
            } else {
                contentSection.classList.add('hidden');
            }
        }

        // Summary
        const summarySection = document.querySelector('#summary-section');
        if (summarySection) {
            if (article.summary || article.summary_english) {
                summarySection.classList.remove('hidden');
                this.updateContentText('summary-zh', article.summary);
                this.updateContentText('summary-en', article.summary_english);
            } else {
                summarySection.classList.add('hidden');
            }
        }

        this.toggleLanguageContent();
    }

    updateContentText(id, content) {
        const element = document.getElementById(id);
        if (element && content) {
            element.textContent = content;
            element.parentElement.classList.remove('hidden');
        } else if (element) {
            element.parentElement.classList.add('hidden');
        }
    }

    updateActionButtons(article) {
        const scrapeBtn = document.querySelector('[data-action="scrape-content"]');
        const summaryBtn = document.querySelector('[data-action="generate-summary"]');
        
        if (scrapeBtn) {
            scrapeBtn.disabled = article.is_content_scraped;
            scrapeBtn.textContent = article.is_content_scraped ? 'Content Scraped' : 'Scrape Content';
        }
        
        if (summaryBtn) {
            summaryBtn.disabled = !article.is_content_scraped || article.is_summarized;
            summaryBtn.textContent = article.is_summarized ? 'Summary Generated' : 'Generate Summary';
        }
    }

    async handleScrapeContent(button) {
        if (!this.currentArticleId) return;

        this.setButtonLoading(button, 'Scraping...');
        
        try {
            const response = await fetch(`/api/content/scrape/${this.currentArticleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showMessage('Content scraping started successfully', 'success');
                this.pollScrapingStatus();
            } else {
                throw new Error(result.detail || 'Scraping failed');
            }
        } catch (error) {
            console.error('Scraping error:', error);
            this.showMessage(error.message, 'error');
        } finally {
            this.resetButton(button, 'Scrape Content');
        }
    }

    async handleGenerateSummary(button) {
        if (!this.currentArticleId) return;

        this.setButtonLoading(button, 'Generating...');
        
        try {
            const response = await fetch(`/api/content/summarize/${this.currentArticleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showMessage('Summary generation started', 'success');
                this.pollSummaryStatus();
            } else {
                throw new Error(result.detail || 'Summary generation failed');
            }
        } catch (error) {
            console.error('Summary error:', error);
            this.showMessage(error.message, 'error');
        } finally {
            this.resetButton(button, 'Generate Summary');
        }
    }

    async handleSaveToCategory(button) {
        const selectedCategory = document.querySelector('.category-card.selected');
        if (!selectedCategory || !this.currentArticleId) {
            this.showMessage('Please select a category first', 'warning');
            return;
        }

        const categoryId = selectedCategory.dataset.categoryId;
        this.setButtonLoading(button, 'Saving...');

        try {
            const response = await fetch('/api/categories/save-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    news_id: this.currentArticleId,
                    category_id: parseInt(categoryId),
                    custom_title: document.querySelector('.article-title').textContent,
                    notes: ""
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showMessage('Article saved to category successfully', 'success');
                selectedCategory.classList.add('saved');
            } else {
                throw new Error(result.detail || 'Failed to save to category');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showMessage(error.message, 'error');
        } finally {
            this.resetButton(button, 'Save to Category');
        }
    }

    handleLanguageToggle(button) {
        const language = button.dataset.lang;
        if (language === this.currentLanguage) return;

        // Update button states
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        this.currentLanguage = language;
        this.toggleLanguageContent();
    }

    toggleLanguageContent() {
        const chineseElements = document.querySelectorAll('[data-lang="zh"]');
        const englishElements = document.querySelectorAll('[data-lang="en"]');

        chineseElements.forEach(el => {
            el.classList.toggle('hidden', this.currentLanguage !== 'zh');
        });

        englishElements.forEach(el => {
            el.classList.toggle('hidden', this.currentLanguage !== 'en');
        });
    }

    initializeLanguageToggle() {
        const toggleContainer = document.querySelector('.language-toggle');
        if (toggleContainer) {
            const zhBtn = toggleContainer.querySelector('[data-lang="zh"]');
            if (zhBtn) {
                zhBtn.classList.add('active');
            }
        }
    }

    handleCategorySelect(card) {
        // Remove previous selection
        document.querySelectorAll('.category-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // Add selection to clicked card
        card.classList.add('selected');
    }

    async pollScrapingStatus() {
        if (!this.currentArticleId) return;

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/content/status/${this.currentArticleId}`);
                const status = await response.json();
                
                if (status.is_content_scraped) {
                    clearInterval(pollInterval);
                    this.loadArticleDetails(this.currentArticleId);
                    this.showMessage('Content scraping completed!', 'success');
                }
            } catch (error) {
                console.error('Status polling error:', error);
                clearInterval(pollInterval);
            }
        }, 2000);

        // Auto-clear after 30 seconds
        setTimeout(() => clearInterval(pollInterval), 30000);
    }

    async pollSummaryStatus() {
        if (!this.currentArticleId) return;

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/content/status/${this.currentArticleId}`);
                const status = await response.json();
                
                if (status.is_summarized) {
                    clearInterval(pollInterval);
                    this.loadArticleDetails(this.currentArticleId);
                    this.showMessage('Summary generation completed!', 'success');
                }
            } catch (error) {
                console.error('Summary polling error:', error);
                clearInterval(pollInterval);
            }
        }, 3000);

        // Auto-clear after 60 seconds
        setTimeout(() => clearInterval(pollInterval), 60000);
    }

    startStatusPolling() {
        // Poll every 10 seconds for any updates
        setInterval(() => {
            if (this.currentArticleId) {
                this.loadArticleDetails(this.currentArticleId);
            }
        }, 10000);
    }

    setButtonLoading(button, text) {
        button.disabled = true;
        button.innerHTML = `<div class="spinner"></div> ${text}`;
    }

    resetButton(button, text) {
        button.disabled = false;
        button.innerHTML = text;
    }

    showMessage(message, type = 'info') {
        const container = document.querySelector('.article-detail');
        if (!container) return;

        // Remove existing messages
        const existingMessages = container.querySelectorAll('.error-message, .success-message, .warning-message');
        existingMessages.forEach(msg => msg.remove());

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        messageDiv.textContent = message;

        // Insert at the top of the article detail
        container.insertBefore(messageDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            const categories = await response.json();
            this.renderCategories(categories);
        } catch (error) {
            console.error('Failed to load categories:', error);
        }
    }

    renderCategories(categories) {
        const grid = document.querySelector('.category-grid');
        if (!grid) return;

        grid.innerHTML = categories.map(category => `
            <div class="category-card" data-category-id="${category.id}">
                <div class="category-name">${category.name}</div>
                <div class="category-description">${category.description}</div>
            </div>
        `).join('');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.contentManager = new ContentManager();
});

// Export for use in other scripts
window.ContentManager = ContentManager; 