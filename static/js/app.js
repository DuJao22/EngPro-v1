/**
 * CivilSaaS JavaScript Application
 * Main application JavaScript file
 */

// Global application object
const CivilSaaS = {
    // Application configuration
    config: {
        version: '1.0.0',
        apiBaseUrl: '/api',
        debounceDelay: 300,
        toastDuration: 5000
    },

    // Initialize application
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupFormValidation();
        this.setupFileUploads();
        this.setupTooltips();
        this.setupModals();
        this.setupMobileOptimizations();
        this.setupTouchGestures();
        this.setupResponsiveFeatures();
        this.setupLogoDetection();
        console.log('EngenPro Application initialized');
    },

    // Setup global event listeners
    setupEventListeners() {
        // Auto-hide alerts
        document.addEventListener('DOMContentLoaded', () => {
            const alerts = document.querySelectorAll('.alert-dismissible');
            alerts.forEach(alert => {
                setTimeout(() => {
                    const closeBtn = alert.querySelector('.btn-close');
                    if (closeBtn) {
                        closeBtn.click();
                    }
                }, this.config.toastDuration);
            });
        });

        // Confirm delete buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-confirm-delete]')) {
                e.preventDefault();
                const message = e.target.getAttribute('data-confirm-delete') || 'Tem certeza que deseja excluir este item?';
                if (confirm(message)) {
                    const form = e.target.closest('form');
                    if (form) {
                        form.submit();
                    } else {
                        window.location.href = e.target.href;
                    }
                }
            }
        });

        // Auto-save forms
        document.addEventListener('input', this.debounce((e) => {
            if (e.target.matches('[data-auto-save]')) {
                this.autoSave(e.target.closest('form'));
            }
        }, this.config.debounceDelay));

        // Dynamic form calculations
        document.addEventListener('input', (e) => {
            if (e.target.matches('[data-calculate]')) {
                this.performCalculation(e.target);
            }
        });
    },

    // Initialize Bootstrap components
    initializeComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

        // Initialize dropdowns manually to ensure they work
        const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        dropdownElementList.map(dropdownToggleEl => new bootstrap.Dropdown(dropdownToggleEl));

        // Initialize progress bars with animation
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.getAttribute('aria-valuenow');
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width + '%';
            }, 100);
        });
    },

    // Setup form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Custom validation rules
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateEmail(input);
            });
        });

        const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="phone"]');
        phoneInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validatePhone(input);
            });
        });
    },

    // Setup file upload enhancements
    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            // Create drop zone
            this.createDropZone(input);
            
            // File validation
            input.addEventListener('change', (e) => {
                this.validateFiles(e.target);
            });
        });
    },

    // Create drag and drop zone for file inputs
    createDropZone(fileInput) {
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload-area';
        wrapper.innerHTML = `
            <i class="fas fa-cloud-upload-alt fa-2x text-muted mb-2"></i>
            <p class="mb-0">Arraste arquivos aqui ou clique para selecionar</p>
            <small class="text-muted">Formatos aceitos: ${fileInput.accept || 'Todos'}</small>
        `;

        fileInput.parentNode.insertBefore(wrapper, fileInput.nextSibling);
        wrapper.appendChild(fileInput);
        fileInput.style.display = 'none';

        // Event listeners
        wrapper.addEventListener('click', () => fileInput.click());
        wrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            wrapper.classList.add('dragover');
        });
        wrapper.addEventListener('dragleave', () => {
            wrapper.classList.remove('dragover');
        });
        wrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            wrapper.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            this.validateFiles(fileInput);
        });
    },

    // Validate uploaded files
    validateFiles(fileInput) {
        const files = Array.from(fileInput.files);
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = fileInput.accept ? fileInput.accept.split(',').map(t => t.trim()) : [];

        files.forEach(file => {
            if (file.size > maxSize) {
                this.showNotification('Arquivo muito grande. Máximo: 10MB', 'error');
                fileInput.value = '';
                return;
            }

            if (allowedTypes.length && !allowedTypes.some(type => {
                if (type.startsWith('.')) {
                    return file.name.toLowerCase().endsWith(type.toLowerCase());
                }
                return file.type.match(type.replace('*', '.*'));
            })) {
                this.showNotification('Tipo de arquivo não permitido', 'error');
                fileInput.value = '';
                return;
            }
        });

        // Update drop zone text
        const dropZone = fileInput.closest('.file-upload-area');
        if (dropZone && files.length > 0) {
            const fileList = files.map(f => f.name).join(', ');
            dropZone.querySelector('p').textContent = `Arquivos selecionados: ${fileList}`;
        }
    },

    // Setup tooltips and help text
    setupTooltips() {
        // Add help tooltips to form labels
        const helpTexts = {
            'cnpj_id': 'Formato: 00.000.000/0000-00',
            'phone': 'Formato: (11) 99999-9999',
            'probability': 'Escala de 1 (muito baixa) a 5 (muito alta)',
            'impact': 'Escala de 1 (muito baixo) a 5 (muito alto)',
            'carbon_emissions_per_unit': 'Emissões em kg de CO₂ por unidade do material'
        };

        Object.entries(helpTexts).forEach(([fieldName, helpText]) => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const label = document.querySelector(`label[for="${field.id}"]`);
                if (label) {
                    const helpIcon = document.createElement('i');
                    helpIcon.className = 'fas fa-question-circle text-muted ms-1';
                    helpIcon.setAttribute('data-bs-toggle', 'tooltip');
                    helpIcon.setAttribute('title', helpText);
                    label.appendChild(helpIcon);
                }
            }
        });
    },

    // Setup modal enhancements
    setupModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const autofocusElement = modal.querySelector('[autofocus]');
                if (autofocusElement) {
                    autofocusElement.focus();
                }
            });
        });
    },

    // Perform dynamic calculations
    performCalculation(element) {
        const calculationType = element.getAttribute('data-calculate');
        
        switch (calculationType) {
            case 'budget-total':
                this.calculateBudgetTotal(element);
                break;
            case 'risk-score':
                this.calculateRiskScore(element);
                break;
            case 'material-emissions':
                this.calculateMaterialEmissions(element);
                break;
            default:
                console.warn('Unknown calculation type:', calculationType);
        }
    },

    // Calculate budget item total
    calculateBudgetTotal(element) {
        const form = element.closest('form');
        const quantity = parseFloat(form.querySelector('[name="quantity"]')?.value) || 0;
        const unitCost = parseFloat(form.querySelector('[name="unit_cost"]')?.value) || 0;
        const totalField = form.querySelector('[name="total_cost"], #total_cost');
        
        if (totalField) {
            const total = quantity * unitCost;
            totalField.value = this.formatCurrency(total);
        }
    },

    // Calculate risk score
    calculateRiskScore(element) {
        const form = element.closest('form');
        const probability = parseInt(form.querySelector('[name="probability"]')?.value) || 1;
        const impact = parseInt(form.querySelector('[name="impact"]')?.value) || 1;
        const scoreField = form.querySelector('#risk_score');
        
        if (scoreField) {
            const score = probability * impact;
            let level = 'Baixo';
            let className = 'text-success';
            
            if (score >= 15) {
                level = 'Alto';
                className = 'text-danger';
            } else if (score >= 6) {
                level = 'Médio';
                className = 'text-warning';
            }
            
            scoreField.value = `${score} (${level})`;
            scoreField.className = `form-control fw-bold ${className}`;
        }
    },

    // Calculate material emissions
    calculateMaterialEmissions(element) {
        const form = element.closest('form');
        const quantity = parseFloat(form.querySelector('[name="quantity"]')?.value) || 0;
        const materialSelect = form.querySelector('[name="material_id"]');
        
        if (materialSelect) {
            const selectedOption = materialSelect.options[materialSelect.selectedIndex];
            const emissions = parseFloat(selectedOption.getAttribute('data-emissions')) || 0;
            const cost = parseFloat(selectedOption.getAttribute('data-cost')) || 0;
            
            const totalEmissions = quantity * emissions;
            const totalCost = quantity * cost;
            
            const emissionsField = form.querySelector('#total_emissions');
            const costField = form.querySelector('#total_cost');
            
            if (emissionsField) {
                emissionsField.value = `${totalEmissions.toFixed(2)} kg CO₂`;
            }
            
            if (costField) {
                costField.value = this.formatCurrency(totalCost);
            }
        }
    },

    // Auto-save form data
    autoSave(form) {
        if (!form) return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const formId = form.id || 'form_' + Date.now();
        
        localStorage.setItem(`autosave_${formId}`, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
        
        this.showNotification('Dados salvos automaticamente', 'info', 2000);
    },

    // Load auto-saved data
    loadAutoSave(form) {
        if (!form) return;
        
        const formId = form.id || 'form_' + Date.now();
        const saved = localStorage.getItem(`autosave_${formId}`);
        
        if (saved) {
            try {
                const { data, timestamp } = JSON.parse(saved);
                const age = Date.now() - timestamp;
                
                // Only load if less than 1 hour old
                if (age < 3600000) {
                    Object.entries(data).forEach(([name, value]) => {
                        const field = form.querySelector(`[name="${name}"]`);
                        if (field && !field.value) {
                            field.value = value;
                        }
                    });
                    
                    this.showNotification('Dados auto-salvos carregados', 'info');
                }
            } catch (e) {
                console.warn('Failed to load auto-saved data:', e);
            }
        }
    },

    // Email validation
    validateEmail(input) {
        const email = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            input.setCustomValidity('Por favor, insira um e-mail válido');
            input.classList.add('is-invalid');
        } else {
            input.setCustomValidity('');
            input.classList.remove('is-invalid');
            if (email) input.classList.add('is-valid');
        }
    },

    // Phone validation
    validatePhone(input) {
        const phone = input.value.replace(/\D/g, '');
        
        if (phone && phone.length < 10) {
            input.setCustomValidity('Telefone deve ter pelo menos 10 dígitos');
            input.classList.add('is-invalid');
        } else {
            input.setCustomValidity('');
            input.classList.remove('is-invalid');
            if (phone) {
                input.classList.add('is-valid');
                // Format phone number
                if (phone.length === 11) {
                    input.value = `(${phone.slice(0,2)}) ${phone.slice(2,7)}-${phone.slice(7)}`;
                } else if (phone.length === 10) {
                    input.value = `(${phone.slice(0,2)}) ${phone.slice(2,6)}-${phone.slice(6)}`;
                }
            }
        }
    },

    // Show notification
    showNotification(message, type = 'info', duration = null) {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto remove
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration || this.config.toastDuration);
    },

    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(amount);
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Utility: Format date for Brazilian locale
    formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
    },

    // Utility: Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Export data to CSV
    exportToCSV(data, filename) {
        const csvContent = data.map(row => 
            Object.values(row).map(field => `"${field}"`).join(',')
        ).join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    // Print page content
    printPage() {
        window.print();
    },

    // Toggle loading state
    toggleLoading(element, loading = true) {
        if (loading) {
            element.disabled = true;
            const originalText = element.textContent;
            element.setAttribute('data-original-text', originalText);
            element.innerHTML = '<span class="loading-spinner me-2"></span>Carregando...';
        } else {
            element.disabled = false;
            const originalText = element.getAttribute('data-original-text');
            if (originalText) {
                element.textContent = originalText;
                element.removeAttribute('data-original-text');
            }
        }
    },

    // ===== MOBILE-SPECIFIC OPTIMIZATIONS ===== //

    // Setup mobile optimizations
    setupMobileOptimizations() {
        // Prevent zoom on input focus for iOS
        if (this.isMobile()) {
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.type !== 'file') {
                    input.style.fontSize = '16px';
                }
            });
        }

        // Optimize touch targets
        this.optimizeTouchTargets();

        // Setup swipe gestures for navigation
        this.setupSwipeNavigation();

        // Optimize viewport for mobile
        this.optimizeViewport();

        // Setup mobile-friendly modals
        this.setupMobileModals();

        // Handle device orientation changes
        this.handleOrientationChange();
    },

    // Setup touch gestures
    setupTouchGestures() {
        if (!this.isMobile()) return;

        // Add touch feedback to interactive elements
        const touchElements = document.querySelectorAll('.btn, .card, .nav-link, .dropdown-item, .table tbody tr');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.style.opacity = '0.7';
                element.style.transform = 'scale(0.98)';
            }, { passive: true });

            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.style.opacity = '';
                    element.style.transform = '';
                }, 150);
            }, { passive: true });

            element.addEventListener('touchcancel', () => {
                element.style.opacity = '';
                element.style.transform = '';
            }, { passive: true });
        });

        // Setup pull-to-refresh gesture (basic implementation)
        this.setupPullToRefresh();
    },

    // Setup responsive features
    setupResponsiveFeatures() {
        // Responsive table scrolling
        this.setupResponsiveTables();

        // Responsive navigation
        this.setupResponsiveNavigation();

        // Responsive forms
        this.setupResponsiveForms();

        // Setup lazy loading for images
        this.setupLazyLoading();

        // Monitor viewport size changes
        this.monitorViewportChanges();
    },

    // Check if device is mobile
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
               window.innerWidth <= 768;
    },

    // Optimize touch targets for mobile
    optimizeTouchTargets() {
        const minTouchSize = 44; // Minimum 44px for accessibility
        
        const elements = document.querySelectorAll('.btn, .nav-link, .dropdown-item, input, select, .form-check-input');
        elements.forEach(element => {
            const rect = element.getBoundingClientRect();
            if (rect.height < minTouchSize) {
                element.style.minHeight = minTouchSize + 'px';
                element.style.display = 'flex';
                element.style.alignItems = 'center';
            }
        });
    },

    // Setup swipe navigation
    setupSwipeNavigation() {
        let startX, startY, distX, distY;
        const threshold = 100; // Minimum distance for swipe
        const restraint = 100; // Maximum distance perpendicular to swipe direction

        document.addEventListener('touchstart', (e) => {
            startX = e.changedTouches[0].pageX;
            startY = e.changedTouches[0].pageY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            distX = e.changedTouches[0].pageX - startX;
            distY = e.changedTouches[0].pageY - startY;

            if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint) {
                if (distX > 0) {
                    // Swipe right - go back if possible
                    if (window.history.length > 1) {
                        window.history.back();
                    }
                } else {
                    // Swipe left - could implement forward navigation
                    console.log('Swipe left detected');
                }
            }
        }, { passive: true });
    },

    // Optimize viewport
    optimizeViewport() {
        // Prevent horizontal scrolling
        document.documentElement.style.overflowX = 'hidden';
        document.body.style.overflowX = 'hidden';

        // Optimize for mobile browsers
        if (this.isMobile()) {
            // Hide address bar on scroll
            let ticking = false;
            const hideAddressBar = () => {
                if (!ticking) {
                    requestAnimationFrame(() => {
                        if (window.scrollY > 50) {
                            document.body.classList.add('scrolling');
                        } else {
                            document.body.classList.remove('scrolling');
                        }
                        ticking = false;
                    });
                    ticking = true;
                }
            };

            window.addEventListener('scroll', hideAddressBar, { passive: true });
        }
    },

    // Setup mobile-friendly modals
    setupMobileModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (this.isMobile()) {
                modal.classList.add('modal-fullscreen-sm-down');
                
                // Add close button for easier access
                const modalHeader = modal.querySelector('.modal-header');
                if (modalHeader && !modalHeader.querySelector('.btn-close')) {
                    const closeBtn = document.createElement('button');
                    closeBtn.type = 'button';
                    closeBtn.className = 'btn-close';
                    closeBtn.setAttribute('data-bs-dismiss', 'modal');
                    modalHeader.appendChild(closeBtn);
                }
            }
        });
    },

    // Handle device orientation changes
    handleOrientationChange() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Force re-calculation of viewport height
                document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
                
                // Refresh responsive components
                this.setupResponsiveTables();
                this.optimizeTouchTargets();
            }, 100);
        });

        // Set initial viewport height
        document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    },

    // Setup pull-to-refresh
    setupPullToRefresh() {
        let startY, currentY, pullDistance;
        const threshold = 80; // Distance to trigger refresh
        const maxPull = 120; // Maximum pull distance

        const refreshIndicator = document.createElement('div');
        refreshIndicator.className = 'pull-to-refresh-indicator';
        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt"></i> Puxe para atualizar';
        refreshIndicator.style.cssText = `
            position: fixed;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 9999;
            transition: all 0.3s ease;
            font-size: 14px;
        `;
        document.body.appendChild(refreshIndicator);

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
            }
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY) {
                currentY = e.touches[0].pageY;
                pullDistance = Math.min(currentY - startY, maxPull);
                
                if (pullDistance > 0) {
                    refreshIndicator.style.top = `${Math.min(pullDistance - 60, 20)}px`;
                    refreshIndicator.style.opacity = Math.min(pullDistance / threshold, 1);
                    
                    if (pullDistance >= threshold) {
                        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Solte para atualizar';
                    } else {
                        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt"></i> Puxe para atualizar';
                    }
                }
            }
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (pullDistance >= threshold) {
                // Trigger page refresh
                window.location.reload();
            } else {
                // Reset indicator
                refreshIndicator.style.top = '-60px';
                refreshIndicator.style.opacity = '0';
            }
            startY = null;
            pullDistance = 0;
        }, { passive: true });
    },

    // Setup responsive tables
    setupResponsiveTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            if (!table.closest('.table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }

            // Add mobile-friendly table features
            if (this.isMobile()) {
                table.classList.add('table-sm');
                
                // Make table headers sticky
                const thead = table.querySelector('thead');
                if (thead) {
                    thead.style.position = 'sticky';
                    thead.style.top = '0';
                    thead.style.zIndex = '10';
                }
            }
        });
    },

    // Setup responsive navigation
    setupResponsiveNavigation() {
        const navbar = document.querySelector('.navbar');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbar && navbarCollapse && this.isMobile()) {
            // Close mobile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
                    const toggleButton = navbar.querySelector('.navbar-toggler');
                    if (toggleButton) {
                        toggleButton.click();
                    }
                }
            });

            // Close mobile menu when clicking on links
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    const toggleButton = navbar.querySelector('.navbar-toggler');
                    if (toggleButton && navbarCollapse.classList.contains('show')) {
                        setTimeout(() => toggleButton.click(), 100);
                    }
                });
            });
        }
    },

    // Setup responsive forms
    setupResponsiveForms() {
        if (this.isMobile()) {
            // Stack form groups vertically on mobile
            const formRows = document.querySelectorAll('.row');
            formRows.forEach(row => {
                if (row.querySelectorAll('.col-md-6').length > 0) {
                    row.querySelectorAll('.col-md-6').forEach(col => {
                        col.className = col.className.replace('col-md-6', 'col-12');
                    });
                }
            });

            // Optimize button groups for mobile
            const btnGroups = document.querySelectorAll('.btn-group');
            btnGroups.forEach(group => {
                group.classList.add('btn-group-vertical');
                group.classList.remove('btn-group');
            });
        }
    },

    // Setup lazy loading for images
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    },

    // Monitor viewport changes
    monitorViewportChanges() {
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                // Re-initialize responsive features on significant size changes
                this.setupResponsiveTables();
                this.setupResponsiveForms();
                this.optimizeTouchTargets();
                
                // Update CSS custom property for viewport height
                document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
            }, 250);
        });
    },

    // Setup logo detection and auto-display
    setupLogoDetection() {
        const logo = document.getElementById('navbar-logo');
        const icon = document.getElementById('navbar-icon');
        
        if (logo && icon) {
            // Check if logo loads successfully
            logo.addEventListener('load', () => {
                logo.style.display = 'block';
                logo.classList.add('loaded');
                icon.style.display = 'none';
                console.log('Logo carregada com sucesso');
            });

            // Handle logo load error (file doesn't exist)
            logo.addEventListener('error', () => {
                logo.style.display = 'none';
                icon.style.display = 'inline';
                console.log('Logo não encontrada, usando ícone padrão');
            });

            // Force check if logo already loaded
            if (logo.complete && logo.naturalHeight !== 0) {
                logo.style.display = 'block';
                logo.classList.add('loaded');
                icon.style.display = 'none';
            }
        }
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    CivilSaaS.init();
});

// Global functions for backward compatibility
window.confirmDelete = function(id, name, url) {
    if (confirm(`Tem certeza que deseja excluir "${name}"?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url || '#';
        document.body.appendChild(form);
        form.submit();
    }
};

// Export CivilSaaS for global access
window.CivilSaaS = CivilSaaS;
