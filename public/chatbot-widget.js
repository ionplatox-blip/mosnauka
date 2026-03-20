/**
 * МОСНАУКА — Chatbot Consultation Widget
 * Standalone script: include on any page to add floating chat bot
 */
(function() {
    'use strict';

    // ── Chunk 1: CSS + Floating Button ──

    const STYLES = `
        /* Chatbot Widget Styles */
        #mn-chat-btn {
            position: fixed;
            bottom: 2rem;
            right: 6rem;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF003C, #cc0030);
            color: white;
            border: none;
            cursor: pointer;
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 24px rgba(255,0,60,0.5);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        #mn-chat-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 32px rgba(255,0,60,0.6);
        }
        #mn-chat-btn .mn-chat-icon {
            font-size: 24px;
            transition: transform 0.3s;
        }
        #mn-chat-btn.mn-open .mn-chat-icon {
            transform: rotate(90deg);
        }
        /* Pulse ring */
        #mn-chat-btn::before {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            border: 2px solid rgba(255,0,60,0.4);
            animation: mn-pulse 2s ease-out infinite;
        }
        @keyframes mn-pulse {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(1.5); opacity: 0; }
        }
        /* Badge */
        #mn-chat-badge {
            position: absolute;
            top: -2px;
            right: -2px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #fff;
            color: #FF003C;
            font-size: 11px;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #FF003C;
        }

        /* ── Chunk 2: Chat Window ── */
        #mn-chat-window {
            position: fixed;
            bottom: 6rem;
            right: 6rem;
            width: 380px;
            max-height: 520px;
            border-radius: 20px;
            background: rgba(15,15,15,0.95);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(255,0,60,0.1);
            z-index: 9997;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transform: translateY(20px) scale(0.95);
            opacity: 0;
            pointer-events: none;
            transition: transform 0.3s ease, opacity 0.3s ease;
        }
        #mn-chat-window.mn-visible {
            transform: translateY(0) scale(1);
            opacity: 1;
            pointer-events: auto;
        }
        /* Header */
        .mn-chat-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            background: rgba(255,0,60,0.08);
        }
        .mn-chat-header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .mn-chat-header-avatar {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: linear-gradient(135deg, #FF003C, #cc0030);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        .mn-chat-header-title {
            font-size: 13px;
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.02em;
        }
        .mn-chat-header-sub {
            font-size: 9px;
            color: rgba(255,255,255,0.4);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        }
        .mn-chat-close {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            background: transparent;
            color: rgba(255,255,255,0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            transition: all 0.2s;
        }
        .mn-chat-close:hover {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        /* Messages area */
        .mn-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-height: 280px;
            max-height: 340px;
        }
        /* Input bar */
        .mn-chat-input-bar {
            display: flex;
            gap: 8px;
            padding: 12px 16px;
            border-top: 1px solid rgba(255,255,255,0.06);
            background: rgba(0,0,0,0.3);
        }
        .mn-chat-input {
            flex: 1;
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 13px;
            font-family: Inter, system-ui, sans-serif;
            outline: none;
            transition: border-color 0.2s;
        }
        .mn-chat-input::placeholder {
            color: rgba(255,255,255,0.25);
        }
        .mn-chat-input:focus {
            border-color: rgba(255,0,60,0.5);
        }
        .mn-chat-send {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: linear-gradient(135deg, #FF003C, #cc0030);
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .mn-chat-send:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 16px rgba(255,0,60,0.4);
        }

        /* ── Chunk 3: Message Bubbles + Chips ── */
        .mn-msg {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.5;
            animation: mn-msg-in 0.3s ease;
        }
        @keyframes mn-msg-in {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .mn-msg-bot {
            align-self: flex-start;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            color: rgba(255,255,255,0.85);
            border-bottom-left-radius: 4px;
        }
        .mn-msg-user {
            align-self: flex-end;
            background: rgba(255,0,60,0.15);
            border: 1px solid rgba(255,0,60,0.2);
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        .mn-msg-bot .mn-msg-label {
            font-size: 9px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: rgba(255,0,60,0.7);
            margin-bottom: 4px;
        }
        /* Chips */
        .mn-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-self: flex-start;
        }
        .mn-chip {
            padding: 7px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255,0,60,0.25);
            background: rgba(255,0,60,0.08);
            color: rgba(255,255,255,0.8);
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: Inter, system-ui, sans-serif;
        }
        .mn-chip:hover {
            background: rgba(255,0,60,0.2);
            border-color: rgba(255,0,60,0.5);
            color: #fff;
        }
        /* Typing indicator */
        .mn-typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            align-self: flex-start;
        }
        .mn-typing-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: rgba(255,0,60,0.5);
            animation: mn-dot-bounce 1.4s infinite ease-in-out;
        }
        .mn-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .mn-typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes mn-dot-bounce {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }
    `;

    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = STYLES;
        document.head.appendChild(style);
    }

    function createButton() {
        const btn = document.createElement('button');
        btn.id = 'mn-chat-btn';
        btn.title = 'Консультант МОСНАУКА';
        btn.innerHTML = `
            <span class="mn-chat-icon">💬</span>
            <span id="mn-chat-badge">1</span>
        `;
        btn.addEventListener('click', toggleChat);
        document.body.appendChild(btn);
    }

    // ── Chunk 2: Chat Window ──

    function createChatWindow() {
        const win = document.createElement('div');
        win.id = 'mn-chat-window';
        win.innerHTML = `
            <div class="mn-chat-header">
                <div class="mn-chat-header-left">
                    <div class="mn-chat-header-avatar">🤖</div>
                    <div>
                        <div class="mn-chat-header-title">МОСНАУКА</div>
                        <div class="mn-chat-header-sub">AI-Консультант</div>
                    </div>
                </div>
                <button class="mn-chat-close" onclick="document.getElementById('mn-chat-btn').click()" title="Закрыть">✕</button>
            </div>
            <div class="mn-chat-messages" id="mn-chat-messages">
                <!-- Messages injected here (Chunk 3) -->
            </div>
            <div class="mn-chat-input-bar">
                <input class="mn-chat-input" id="mn-chat-input" type="text" placeholder="Задайте вопрос..." autocomplete="off" />
                <button class="mn-chat-send" id="mn-chat-send" title="Отправить">➤</button>
            </div>
        `;
        document.body.appendChild(win);
    }

    // ── Chunk 3: Demo Messages + Chips ──

    function injectDemoMessages() {
        const area = document.getElementById('mn-chat-messages');
        area.innerHTML = `
            <div class="mn-msg mn-msg-bot">
                <div class="mn-msg-label">Консультант</div>
                Здравствуйте! Я — AI-консультант платформы <b>МОСНАУКА</b>. Помогу вам с вопросами по НИОКР, налоговым льготам и подбору исполнителей.
            </div>
            <div class="mn-msg mn-msg-bot">
                <div class="mn-msg-label">Консультант</div>
                Чем могу помочь? Выберите тему или задайте вопрос:
            </div>
            <div class="mn-chips">
                <button class="mn-chip" data-q="Как получить налоговую льготу ×2 на НИОКР?">💰 Налоговая льгота ×2</button>
                <button class="mn-chip" data-q="Как подобрать исполнителя НИОКР?">🔍 Подобрать исполнителя</button>
                <button class="mn-chip" data-q="Как оформить НИОКР через платформу?">📝 Оформить НИОКР</button>
            </div>
        `;
    }

    // ── Chunk 4: Input Logic + Mock Reply ──

    const MOCK_REPLIES = {
        'Как получить налоговую льготу ×2 на НИОКР?':
            'Согласно <b>ст. 262 НК РФ</b>, расходы на НИОКР можно учесть с коэффициентом <b>×2</b> при расчёте налога на прибыль.<br><br><b>Условия:</b><br>• НИОКР входит в Перечень №988 Правительства РФ<br>• Подрядчик — аккредитованная научная организация<br>• Оформлены: договор, ТЗ, акт, отчёт<br>• Результаты зарегистрированы в ЕГИСУ НИОКР<br><br>Экономия может составить до <b>5 млн ₽ на 10 млн ₽</b> затрат. Хотите подробную инструкцию?',

        'Как подобрать исполнителя НИОКР?':
            'МОСНАУКА поможет найти оптимального исполнителя:<br><br><b>1.</b> Опишите задачу в поисковой строке или загрузите ТЗ<br><b>2.</b> AI-система подберёт R&D центры и учёных по компетенциям<br><b>3.</b> Сравните предложения и начните переговоры прямо на платформе<br><br>В базе <b>30+ научных центров Москвы</b> и <b>4 500+ учёных</b> с верифицированными компетенциями.<br><br>Начать поиск прямо сейчас? Перейдите в раздел <b>«AI-поиск»</b>.',

        'Как оформить НИОКР через платформу?':
            'Процесс оформления НИОКР на платформе:<br><br><b>1. Подбор</b> — опишите задачу, AI найдёт подходящие центры<br><b>2. Переговоры</b> — обсудите ТЗ, сроки и бюджет в чате<br><b>3. Договор</b> — используйте готовые шаблоны документов<br><b>4. Выполнение</b> — отслеживайте прогресс в личном кабинете<br><b>5. Закрытие</b> — оформите акты и подайте на льготу ×2<br><br>МОСНАУКА сопровождает на всех этапах. Хотите начать?',
    };

    const DEFAULT_REPLY = 'Спасибо за вопрос! Сейчас я работаю в демо-режиме. В полной версии платформы AI-консультант ответит на любые вопросы по НИОКР, налоговым льготам и подбору исполнителей.<br><br>Оставьте контакт, и наш специалист свяжется с вами.';

    function addMessage(text, type) {
        const area = document.getElementById('mn-chat-messages');
        const div = document.createElement('div');
        div.className = 'mn-msg mn-msg-' + type;
        if (type === 'bot') {
            div.innerHTML = '<div class="mn-msg-label">Консультант</div>' + text;
        } else {
            div.textContent = text;
        }
        area.appendChild(div);
        area.scrollTop = area.scrollHeight;
    }

    function showTyping() {
        const area = document.getElementById('mn-chat-messages');
        const t = document.createElement('div');
        t.className = 'mn-typing';
        t.id = 'mn-typing-indicator';
        t.innerHTML = '<div class="mn-typing-dot"></div><div class="mn-typing-dot"></div><div class="mn-typing-dot"></div>';
        area.appendChild(t);
        area.scrollTop = area.scrollHeight;
    }

    function hideTyping() {
        const t = document.getElementById('mn-typing-indicator');
        if (t) t.remove();
    }

    function handleSend(text) {
        if (!text || !text.trim()) return;
        text = text.trim();

        // Show user message
        addMessage(text, 'user');

        // Clear input
        const input = document.getElementById('mn-chat-input');
        if (input) input.value = '';

        // Remove chips after first interaction
        const chips = document.querySelector('.mn-chips');
        if (chips) chips.remove();

        // Show typing, then reply
        showTyping();
        const reply = MOCK_REPLIES[text] || DEFAULT_REPLY;
        setTimeout(function() {
            hideTyping();
            addMessage(reply, 'bot');
        }, 1500);
    }

    function wireInputEvents() {
        // Send button
        document.getElementById('mn-chat-send').addEventListener('click', function() {
            handleSend(document.getElementById('mn-chat-input').value);
        });

        // Enter key
        document.getElementById('mn-chat-input').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSend(this.value);
            }
        });

        // Chip clicks (delegated)
        document.getElementById('mn-chat-messages').addEventListener('click', function(e) {
            const chip = e.target.closest('.mn-chip');
            if (chip) {
                handleSend(chip.getAttribute('data-q'));
            }
        });
    }

    let chatOpen = false;
    function toggleChat() {
        chatOpen = !chatOpen;
        const btn = document.getElementById('mn-chat-btn');
        const win = document.getElementById('mn-chat-window');
        if (chatOpen) {
            btn.classList.add('mn-open');
            btn.querySelector('.mn-chat-icon').textContent = '✕';
            document.getElementById('mn-chat-badge').style.display = 'none';
            win.classList.add('mn-visible');
            // Stop pulse animation when open
            btn.style.setProperty('--mn-pulse-display', 'none');
        } else {
            btn.classList.remove('mn-open');
            btn.querySelector('.mn-chat-icon').textContent = '💬';
            win.classList.remove('mn-visible');
        }
    }

    // ── Init ──
    document.addEventListener('DOMContentLoaded', function() {
        injectStyles();
        createButton();
        createChatWindow();
        injectDemoMessages();
        wireInputEvents();
    });

})();
