document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 加载保存的数据
    loadSavedData();

    // 加载保存的主题和颜色
    loadThemeAndColor();

    // 添加课程按钮点击事件
    document.getElementById('addCourseBtn').addEventListener('click', function() {
        addCourse();
        updateJsonPreview();
    });

    // 复制按钮点击事件
    document.getElementById('copyBtn').addEventListener('click', function() {
        const jsonText = document.getElementById('jsonPreview').textContent;
        navigator.clipboard.writeText(jsonText).then(function() {
            // 显示成功提示
            const toast = new bootstrap.Toast(document.getElementById('copySuccess'));
            toast.show();
            
            // 临时改变按钮样式，提供视觉反馈
            const copyBtn = document.getElementById('copyBtn');
            copyBtn.classList.remove('btn-outline-primary');
            copyBtn.classList.add('btn-success');
            copyBtn.innerHTML = '<i class="bi bi-check-circle"></i> 已复制';
            
            // 2秒后恢复按钮样式
            setTimeout(function() {
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-primary');
                copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> 复制';
            }, 2000);
        }).catch(function(err) {
            console.error('复制失败: ', err);
            alert('复制失败，请手动复制配置。');
        });
    });

    // 监听表单变化
    document.getElementById('configForm').addEventListener('input', function() {
        updateJsonPreview();
        saveData();
    });

    // 监听课程容器变化
    const coursesContainer = document.getElementById('coursesContainer');
    const observer = new MutationObserver(function() {
        updateJsonPreview();
        saveData();
    });
    observer.observe(coursesContainer, { childList: true, subtree: true });

    // 初始添加一个空课程
    if (document.querySelectorAll('.course-card').length === 0) {
        addCourse();
    }

    // 初始化JSON预览
    updateJsonPreview();

    // 主题切换按钮点击事件
    document.getElementById('themeToggle').addEventListener('click', function() {
        toggleTheme();
    });

    // 颜色选择器点击事件
    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            const color = this.getAttribute('data-color');
            changeThemeColor(color);
        });
    });
});

// 添加课程
function addCourse() {
    const coursesContainer = document.getElementById('coursesContainer');
    const template = document.getElementById('courseTemplate').innerHTML;
    const courseId = Date.now();
    const courseNumber = coursesContainer.children.length + 1;
    
    const courseHtml = template
        .replace(/{id}/g, courseId)
        .replace(/{number}/g, courseNumber);
    
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = courseHtml;
    const courseElement = tempDiv.firstElementChild;
    
    coursesContainer.appendChild(courseElement);
    
    // 添加删除课程事件
    courseElement.querySelector('.btn-remove-course').addEventListener('click', function() {
        coursesContainer.removeChild(courseElement);
        // 更新所有课程的编号
        updateCourseNumbers();
        updateJsonPreview();
        saveData();
    });
    
    // 添加课程字段变化事件
    const courseFields = courseElement.querySelectorAll('.course-field');
    courseFields.forEach(field => {
        field.addEventListener('input', function() {
            updateJsonPreview();
            saveData();
        });
    });
}

// 更新课程编号
function updateCourseNumbers() {
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach((card, index) => {
        const heading = card.querySelector('h5');
        heading.textContent = `课程 #${index + 1}`;
    });
}

// 更新JSON预览
function updateJsonPreview() {
    const config = {
        user_account: document.getElementById('userAccount').value,
        user_password: document.getElementById('userPassword').value,
        select_semester: document.getElementById('selectSemester').value,
        dingtalk_webhook: document.getElementById('dingtalkWebhook').value,
        dingtalk_secret: document.getElementById('dingtalkSecret').value,
        feishu_webhook: document.getElementById('feishuWebhook').value,
        feishu_secret: document.getElementById('feishuSecret').value,
        mode: document.getElementById('mode').value,
        courses: []
    };
    
    // 收集课程数据
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        const course = {};
        const fields = card.querySelectorAll('.course-field');
        
        fields.forEach(field => {
            const fieldName = field.getAttribute('data-field');
            const fieldValue = field.value;
            if (fieldValue) {
                course[fieldName] = fieldValue;
            }
        });
        
        if (Object.keys(course).length > 0) {
            config.courses.push(course);
        }
    });
    
    // 更新JSON预览
    const jsonPreview = document.getElementById('jsonPreview');
    jsonPreview.textContent = JSON.stringify(config, null, 4);
}

// 保存数据到本地存储
function saveData() {
    const formData = {
        userAccount: document.getElementById('userAccount').value,
        userPassword: document.getElementById('userPassword').value,
        selectSemester: document.getElementById('selectSemester').value,
        dingtalkWebhook: document.getElementById('dingtalkWebhook').value,
        dingtalkSecret: document.getElementById('dingtalkSecret').value,
        feishuWebhook: document.getElementById('feishuWebhook').value,
        feishuSecret: document.getElementById('feishuSecret').value,
        mode: document.getElementById('mode').value,
        courses: []
    };
    
    // 收集课程数据
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        const course = {};
        const fields = card.querySelectorAll('.course-field');
        
        fields.forEach(field => {
            const fieldName = field.getAttribute('data-field');
            course[fieldName] = field.value;
        });
        
        formData.courses.push(course);
    });
    
    localStorage.setItem('qfnuCourseConfig', JSON.stringify(formData));
}

// 从本地存储加载数据
function loadSavedData() {
    const savedData = localStorage.getItem('qfnuCourseConfig');
    if (!savedData) return;
    
    try {
        const formData = JSON.parse(savedData);
        
        // 填充基本表单
        document.getElementById('userAccount').value = formData.userAccount || '';
        document.getElementById('userPassword').value = formData.userPassword || '';
        document.getElementById('selectSemester').value = formData.selectSemester || '';
        document.getElementById('dingtalkWebhook').value = formData.dingtalkWebhook || '';
        document.getElementById('dingtalkSecret').value = formData.dingtalkSecret || '';
        document.getElementById('feishuWebhook').value = formData.feishuWebhook || '';
        document.getElementById('feishuSecret').value = formData.feishuSecret || '';
        document.getElementById('mode').value = formData.mode || '';
        
        // 添加课程
        const coursesContainer = document.getElementById('coursesContainer');
        coursesContainer.innerHTML = ''; // 清空现有课程
        
        if (formData.courses && formData.courses.length > 0) {
            formData.courses.forEach(courseData => {
                addCourse();
                const courseCard = coursesContainer.lastElementChild;
                
                // 填充课程字段
                Object.keys(courseData).forEach(fieldName => {
                    const field = courseCard.querySelector(`.course-field[data-field="${fieldName}"]`);
                    if (field) {
                        field.value = courseData[fieldName] || '';
                    }
                });
            });
        } else {
            // 如果没有保存的课程，添加一个空课程
            addCourse();
        }
        
        updateJsonPreview();
    } catch (error) {
        console.error('加载保存的数据时出错:', error);
        // 出错时添加一个空课程
        addCourse();
    }
}

// 切换深浅模式
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('qfnuTheme', newTheme);
    
    // 更新图标
    const themeIcon = document.querySelector('#themeToggle i');
    if (newTheme === 'dark') {
        themeIcon.classList.remove('bi-moon-fill');
        themeIcon.classList.add('bi-sun-fill');
    } else {
        themeIcon.classList.remove('bi-sun-fill');
        themeIcon.classList.add('bi-moon-fill');
    }
}

// 更改主题颜色
function changeThemeColor(color) {
    document.documentElement.style.setProperty('--primary-color', color);
    
    // 计算悬停颜色（稍微深一点）
    const hoverColor = adjustColor(color, -20);
    document.documentElement.style.setProperty('--primary-hover', hoverColor);
    
    // 保存颜色设置
    localStorage.setItem('qfnuThemeColor', color);
    localStorage.setItem('qfnuThemeHoverColor', hoverColor);
}

// 加载保存的主题和颜色
function loadThemeAndColor() {
    // 加载主题
    const savedTheme = localStorage.getItem('qfnuTheme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // 更新图标
        const themeIcon = document.querySelector('#themeToggle i');
        if (savedTheme === 'dark') {
            themeIcon.classList.remove('bi-moon-fill');
            themeIcon.classList.add('bi-sun-fill');
        }
    }
    
    // 加载颜色
    const savedColor = localStorage.getItem('qfnuThemeColor');
    const savedHoverColor = localStorage.getItem('qfnuThemeHoverColor');
    
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
    }
    
    if (savedHoverColor) {
        document.documentElement.style.setProperty('--primary-hover', savedHoverColor);
    }
}

// 调整颜色亮度
function adjustColor(color, amount) {
    // 将颜色转换为RGB
    let r, g, b;
    
    if (color.startsWith('#')) {
        const hex = color.substring(1);
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
    } else {
        return color; // 如果不是十六进制颜色，直接返回
    }
    
    // 调整亮度
    r = Math.max(0, Math.min(255, r + amount));
    g = Math.max(0, Math.min(255, g + amount));
    b = Math.max(0, Math.min(255, b + amount));
    
    // 转回十六进制
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
} 