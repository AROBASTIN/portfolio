/* ==========================================================================
   ARO BASTIN - FULL STACK DEVELOPER PORTFOLIO
   Interactive Client Logic
   ========================================================================== */

/* ==========================================================================
   API CONFIGURATION
   - Local Development: Defaults to 'http://127.0.0.1:5000'
   - Production Deployment: Can be overridden via window.PORTFOLIO_API_URL
   ========================================================================== */
const IS_LOCAL_HOST = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1' || 
                      window.location.protocol === 'file:';

const API_BASE_URL = window.PORTFOLIO_API_URL || (
  IS_LOCAL_HOST 
    ? 'http://127.0.0.1:5000' 
    : 'https://portfolio-backend-4adi.onrender.com' // Replace with deployed production Flask API URL (e.g. Render / Railway)
);

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const navbar = document.getElementById('navbar');
  const navMenu = document.getElementById('nav-menu');
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.querySelectorAll('.nav-link');
  const revealElements = document.querySelectorAll('.reveal');
  const contactForm = document.getElementById('contact-form');
  const modalOverlay = document.getElementById('modal-overlay');
  const modalBox = document.getElementById('modal-box');
  const modalClose = document.getElementById('modal-close');
  const toastContainer = document.getElementById('toast-container');

  /* --------------------------------------------------------------------------
     1. Navigation Scroll & Mobile Menu Toggle
     -------------------------------------------------------------------------- */
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
    highlightNavOnScroll();
  });

  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      const icon = mobileToggle.querySelector('i');
      if (navMenu.classList.contains('active')) {
        icon.className = 'fa-solid fa-xmark';
      } else {
        icon.className = 'fa-solid fa-bars';
      }
    });
  }

  // Close mobile menu when nav link is clicked
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        const icon = mobileToggle.querySelector('i');
        if (icon) icon.className = 'fa-solid fa-bars';
      }
    });
  });

  /* --------------------------------------------------------------------------
     2. Active Navigation Highlight on Scroll
     -------------------------------------------------------------------------- */
  function highlightNavOnScroll() {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.pageYOffset;

    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop - 120;
      const sectionId = current.getAttribute('id');
      const navLink = document.querySelector(`.nav-link[href*="${sectionId}"]`);

      if (navLink) {
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
          navLink.classList.add('active');
        } else {
          navLink.classList.remove('active');
        }
      }
    });
  }

  /* --------------------------------------------------------------------------
     3. IntersectionObserver Section Reveal Animations
     -------------------------------------------------------------------------- */
  const observerOptions = {
    threshold: 0.12,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  revealElements.forEach(el => observer.observe(el));

  /* --------------------------------------------------------------------------
     4. Modal System (Resume Preview & Project Demos)
     -------------------------------------------------------------------------- */
  window.openModal = function(title, contentHtml) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-body').innerHTML = contentHtml;
    modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  function closeModal() {
    modalOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
      closeModal();
    }
  });

  /* --------------------------------------------------------------------------
     5. Resume Viewer & Download Handler
     -------------------------------------------------------------------------- */
  const resumeBtn = document.getElementById('download-resume-btn');
  if (resumeBtn) {
    resumeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const resumeHtml = `
        <div style="font-family: var(--font-sans); color: var(--text-primary); line-height: 1.6;">
          <div style="border-bottom: 2px solid var(--accent-cyan); padding-bottom: 1rem; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.8rem; color: #fff; margin-bottom: 0.25rem;">ARO BASTIN</h2>
            <p style="color: var(--accent-cyan); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">FULL STACK DEVELOPER</p>
            <p style="font-size: 0.9rem; color: var(--text-secondary);">
              <i class="fa-solid fa-location-dot" style="color: var(--accent-cyan);"></i> Paramakudi, Tamil Nadu, India | 
              <i class="fa-solid fa-envelope" style="color: var(--accent-cyan);"></i> arobastin5@gmail.com | 
              <i class="fa-solid fa-phone" style="color: var(--accent-cyan);"></i> +91-8098492597
            </p>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.1rem; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Profile Summary</h3>
            <p style="font-size: 0.95rem; color: var(--text-secondary);">
              Computer Science Engineering student with hands-on experience in full-stack web development, Python application development, API integration, databases, and data-driven applications. Experienced in building end-to-end web applications from responsive frontend interfaces to robust backend APIs and database systems.
            </p>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.1rem; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Technical Skills</h3>
            <p style="font-size: 0.92rem; color: var(--text-secondary); margin-bottom: 0.25rem;"><strong>Frontend:</strong> HTML5, CSS3, JavaScript, Responsive Web Design</p>
            <p style="font-size: 0.92rem; color: var(--text-secondary); margin-bottom: 0.25rem;"><strong>Backend:</strong> Python, Flask, Django, Node.js, REST APIs, API Integration</p>
            <p style="font-size: 0.92rem; color: var(--text-secondary); margin-bottom: 0.25rem;"><strong>Databases:</strong> MongoDB, SQLite, SQL</p>
            <p style="font-size: 0.92rem; color: var(--text-secondary);"><strong>Tools & Cloud:</strong> Git, GitHub, VS Code, Figma, Postman, Tableau, Power BI, Google Cloud</p>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.1rem; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Internship Experience</h3>
            <div style="margin-bottom: 0.75rem;">
              <strong style="color: #fff;">Python Developer Intern — Oasis Infobyte</strong> <span style="color: var(--text-muted); float: right;">June 2025 – July 2025</span>
              <ul style="padding-left: 1.25rem; font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem;">
                <li>Developed Python-based projects and practical programming assignments.</li>
                <li>Applied Python concepts to application development tasks.</li>
                <li>Used GitHub for project organization and version control.</li>
              </ul>
            </div>
            <div>
              <strong style="color: #fff;">Data Analytics Intern (Team Leader) — Novitech</strong>
              <ul style="padding-left: 1.25rem; font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem;">
                <li>Led a 3-member team throughout the project coordinating task allocation and progress.</li>
                <li>Performed data cleaning and developed dashboards using Tableau.</li>
              </ul>
            </div>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.1rem; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Education</h3>
            <p style="font-size: 0.95rem; color: #fff; font-weight: 600;">B.E. Computer Science and Engineering</p>
            <p style="font-size: 0.9rem; color: var(--text-secondary);">Syed Ammal Engineering College, Ramanathapuram (2023 – 2027 | Currently Pursuing)</p>
          </div>

          <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <button onclick="window.print()" class="btn-primary" style="flex: 1; justify-content: center;">
              <i class="fa-solid fa-print"></i> Print / Save PDF
            </button>
            <a href="mailto:arobastin5@gmail.com?subject=Full%20Stack%20Developer%20Opportunity%20-%20Aro%20Bastin" class="btn-secondary" style="flex: 1; justify-content: center; text-align: center;">
              <i class="fa-solid fa-paper-plane"></i> Request Custom PDF
            </a>
          </div>
        </div>
      `;
      openModal("Aro Bastin — Official Resume", resumeHtml);
    });
  }

  /* --------------------------------------------------------------------------
     6. Project Interactive Demo Modals
     -------------------------------------------------------------------------- */
  window.showProjectDetails = function(projectId) {
    if (projectId === 'student-growth') {
      const content = `
        <div style="color: var(--text-primary);">
          <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <span class="tech-pill">Python</span>
            <span class="tech-pill">Flask</span>
            <span class="tech-pill">SQLite</span>
            <span class="tech-pill">Responsive Frontend</span>
          </div>
          <h3 style="font-size: 1.3rem; margin-bottom: 0.75rem; color: var(--accent-cyan);">Student Growth, Recovery & Career Guidance System</h3>
          <p style="color: var(--text-secondary); margin-bottom: 1.25rem;">
            A web-based system designed to analyze student academic performance and provide personalized academic recovery and career guidance.
          </p>
          <h4 style="font-size: 1rem; color: #fff; margin-bottom: 0.5rem;">Architecture & Full Stack Integration:</h4>
          <ul style="padding-left: 1.25rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
            <li><strong>Frontend:</strong> Responsive web-based user interface for student data entry and interactive visualization of academic progress.</li>
            <li><strong>Backend:</strong> Flask API engine evaluating weak subjects, detecting academic risk levels, and generating dynamic recovery plans.</li>
            <li><strong>Database:</strong> SQLite database managing relational tables for students, marks, course recommendations, and historical performance metrics.</li>
          </ul>
          <div style="display: flex; gap: 1rem;">
            <a href="https://github.com/AROBASTIN" target="_blank" rel="noopener noreferrer" class="btn-primary" style="flex: 1; justify-content: center;">
              <i class="fa-brands fa-github"></i> View GitHub Repository
            </a>
          </div>
        </div>
      `;
      openModal("Project Architecture — Student Growth System", content);
    } else if (projectId === 'weather-system') {
      const content = `
        <div style="color: var(--text-primary);">
          <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <span class="tech-pill">Python</span>
            <span class="tech-pill">MongoDB</span>
            <span class="tech-pill">Open-Meteo API</span>
            <span class="tech-pill">APScheduler</span>
          </div>
          <h3 style="font-size: 1.3rem; margin-bottom: 0.75rem; color: var(--accent-cyan);">Real-Time Weather Data Collection System</h3>
          <p style="color: var(--text-secondary); margin-bottom: 1.25rem;">
            An automated weather data collection system that retrieves real-time weather information and stores it for further analysis.
          </p>
          <h4 style="font-size: 1rem; color: #fff; margin-bottom: 0.5rem;">Key Architecture & Automation Features:</h4>
          <ul style="padding-left: 1.25rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
            <li><strong>API Integration:</strong> Connects to Open-Meteo REST API for live meteorological data retrieval.</li>
            <li><strong>Automated Pipeline:</strong> Uses APScheduler background daemon to execute automated polling at regular time intervals.</li>
            <li><strong>NoSQL Storage:</strong> Stores unstructured JSON weather payloads across Chennai, Madurai, and Coimbatore into MongoDB document collections.</li>
            <li><strong>Data Processing:</strong> Filters and cleans raw weather attributes for analytics and downstream dashboard reporting.</li>
          </ul>
          <div style="display: flex; gap: 1rem;">
            <a href="https://github.com/AROBASTIN" target="_blank" rel="noopener noreferrer" class="btn-primary" style="flex: 1; justify-content: center;">
              <i class="fa-brands fa-github"></i> View GitHub Repository
            </a>
          </div>
        </div>
      `;
      openModal("Project Architecture — Weather Collection System", content);
    }
  };

  /* --------------------------------------------------------------------------
     7. Toast Notification Utility & Copy To Clipboard
     -------------------------------------------------------------------------- */
  window.showToast = function(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    let iconClass = 'fa-solid fa-circle-check';
    let iconColor = 'var(--accent-emerald)';

    if (type === 'error') {
      iconClass = 'fa-solid fa-circle-exclamation';
      iconColor = '#ef4444';
      toast.style.borderColor = 'rgba(239, 68, 68, 0.4)';
    } else if (type === 'info') {
      iconClass = 'fa-solid fa-circle-info';
      iconColor = 'var(--accent-cyan)';
      toast.style.borderColor = 'var(--border-accent)';
    }

    toast.innerHTML = `
      <i class="${iconClass}" style="color: ${iconColor}; font-size: 1.2rem;"></i>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  };

  window.copyText = function(text, label) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(`${label} copied to clipboard!`, 'success');
    }).catch(() => {
      showToast(`Copy failed. ${text}`, 'info');
    });
  };

  /* --------------------------------------------------------------------------
     8. Contact Form Real Backend Integration & Submission Handler
     -------------------------------------------------------------------------- */
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const nameInput = document.getElementById('form-name');
      const emailInput = document.getElementById('form-email');
      const messageInput = document.getElementById('form-message');
      const honeypotInput = document.getElementById('form-honeypot');

      const name = nameInput ? nameInput.value.trim() : '';
      const email = emailInput ? emailInput.value.trim() : '';
      const message = messageInput ? messageInput.value.trim() : '';
      const honeypot = honeypotInput ? honeypotInput.value.trim() : '';

      // Client-Side Validation
      if (!name) {
        showToast('Please enter your name.', 'error');
        if (nameInput) nameInput.focus();
        return;
      }
      if (name.length < 2) {
        showToast('Name must be at least 2 characters.', 'error');
        if (nameInput) nameInput.focus();
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email) {
        showToast('Please enter your email address.', 'error');
        if (emailInput) emailInput.focus();
        return;
      }
      if (!emailRegex.test(email)) {
        showToast('Please enter a valid email address.', 'error');
        if (emailInput) emailInput.focus();
        return;
      }

      if (!message) {
        showToast('Please enter your message.', 'error');
        if (messageInput) messageInput.focus();
        return;
      }
      if (message.length < 5) {
        showToast('Message must be at least 5 characters long.', 'error');
        if (messageInput) messageInput.focus();
        return;
      }

      // UI Loading State
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalBtnContent = submitBtn ? submitBtn.innerHTML : '<span>Send Message</span> <i class="fa-solid fa-paper-plane"></i>';
      
      if (submitBtn) {
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Sending...</span>`;
        submitBtn.disabled = true;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/contact`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            name: name,
            email: email,
            message: message,
            _honeypot: honeypot
          })
        });

        const data = await response.json().catch(() => null);

        if (response.ok && data && data.success) {
          // Success Feedback
          showToast(data.message || 'Message sent successfully.', 'success');
          
          if (submitBtn) {
            submitBtn.innerHTML = `<i class="fa-solid fa-check"></i> <span>Message Sent!</span>`;
            submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
          }

          // Clear form on success
          contactForm.reset();

          setTimeout(() => {
            if (submitBtn) {
              submitBtn.innerHTML = originalBtnContent;
              submitBtn.style.background = '';
              submitBtn.disabled = false;
            }
          }, 3000);
        } else {
          // Server / Validation / Rate limit error
          const errorMsg = (data && data.message) ? data.message : 'Unable to send your message. Please try again.';
          showToast(errorMsg, 'error');

          if (submitBtn) {
            submitBtn.innerHTML = originalBtnContent;
            submitBtn.disabled = false;
          }
        }
      } catch (err) {
        // Network / CORS / Backend unavailable error
        console.error('Contact form submission error:', err);
        showToast('Unable to connect to the backend server. Please check your connection or try again later.', 'error');
        
        if (submitBtn) {
          submitBtn.innerHTML = originalBtnContent;
          submitBtn.disabled = false;
        }
      }
    });
  }
});
