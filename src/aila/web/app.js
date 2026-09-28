const chatPanel = document.getElementById('chat-panel');
const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

const STORAGE_KEY = 'ai_learning_assistant_thread_id';

function getOrCreateThreadId() {
  let threadId = localStorage.getItem(STORAGE_KEY);
  if (!threadId) {
    threadId = `conversation-${crypto.randomUUID()}`;
    localStorage.setItem(STORAGE_KEY, threadId);
  }
  return threadId;
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderMarkdown(text) {
  if (!text) {
    return '';
  }

  const renderer = new marked.Renderer();
  renderer.code = ({ text: codeText, lang }) => {
    const normalizedLang = (lang || '').toLowerCase();
    const safeLang = hljs.getLanguage(normalizedLang)
      ? normalizedLang
      : 'plaintext';
    const highlighted = hljs.highlight(codeText, {
      language: safeLang,
      ignoreIllegals: true,
    }).value;

    return `<pre><code class="hljs language-${safeLang}">${highlighted}</code></pre>`;
  };

  marked.setOptions({
    renderer,
    gfm: true,
    breaks: false,
    headerIds: false,
    mangle: false,
  });

  try {
    const html = marked.parse(text);
    return DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
      ADD_ATTR: ['target', 'rel'],
      ALLOWED_TAGS: [
        'a', 'b', 'blockquote', 'br', 'code', 'dd', 'del', 'details', 'div', 'dl',
        'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'kbd',
        'li', 'ol', 'p', 'pre', 'q', 's', 'samp', 'small', 'span', 'strike', 'strong',
        'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'tt',
        'u', 'ul'
      ],
    });
  } catch (error) {
    return `<pre>${escapeHtml(text)}</pre>`;
  }
}

function renderAiBubble(bubble, text) {
  bubble.innerHTML = renderMarkdown(text);
  chatPanel.scrollTop = chatPanel.scrollHeight;
}

function formatSourceLabel(entry) {
  const source = entry && entry.source ? String(entry.source) : 'source';
  const page = entry && entry.page != null ? ` · p.${entry.page}` : '';
  return `${source}${page}`;
}

function renderSources(sourcesBox, sources) {
  if (!Array.isArray(sources) || sources.length === 0) {
    sourcesBox.innerHTML = '';
    sourcesBox.hidden = true;
    return;
  }

  const seen = new Set();
  const items = [];

  for (const source of sources) {
    const entry = source && typeof source === 'object' ? source : { source: String(source) };
    const label = formatSourceLabel(entry);
    const key = JSON.stringify({
      source: entry.source || '',
      page: entry.page ?? null,
      title: entry.title ?? '',
      file_name: entry.file_name ?? ''
    });
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    items.push(label);
  }

  if (items.length === 0) {
    sourcesBox.innerHTML = '';
    sourcesBox.hidden = true;
    return;
  }

  sourcesBox.innerHTML = `
    <div class="source-title">参考来源</div>
    <ul class="source-list">
      ${items.map((label) => `<li>${escapeHtml(label)}</li>`).join('')}
    </ul>
  `;
  sourcesBox.hidden = false;
}

function appendMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const label = document.createElement('div');
  label.className = 'message-label';
  label.textContent = role === 'user' ? 'User' : 'AI';

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = text;
  if (role === 'ai') {
    bubble.innerHTML = '';
  }

  const sourcesBox = document.createElement('div');
  sourcesBox.className = 'message-sources';
  sourcesBox.hidden = true;

  wrapper.appendChild(label);
  wrapper.appendChild(bubble);
  if (role === 'ai') {
    wrapper.appendChild(sourcesBox);
  }

  chatPanel.appendChild(wrapper);
  chatPanel.scrollTop = chatPanel.scrollHeight;
  return { wrapper, bubble, sourcesBox };
}

function setSendingState(isSending) {
  sendButton.disabled = isSending;
  input.disabled = isSending;
  if (isSending) {
    sendButton.textContent = '生成中...';
  } else {
    sendButton.textContent = '发送';
  }
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) {
    return;
  }

  const threadId = getOrCreateThreadId();
  appendMessage('user', message);

  const aiMessage = {
    type: 'ai',
    content: '',
    sources: [],
  };
  const aiBlock = appendMessage('ai', '');
  const aiBubble = aiBlock.bubble;
  const aiSourcesBox = aiBlock.sourcesBox;

  setSendingState(true);
  input.value = '';

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        thread_id: threadId,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error('Request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data:')) {
          continue;
        }

        const raw = line.slice(5).trim();
        if (!raw) {
          continue;
        }

        try {
          const payload = JSON.parse(raw);
          if (typeof payload.content === 'string') {
            aiMessage.content += payload.content;
            renderAiBubble(aiBubble, aiMessage.content);
          }

          if (payload && payload.source && typeof payload.source === 'object') {
            const nextSource = payload.source;
            const hasDuplicate = aiMessage.sources.some((source) => JSON.stringify(source) === JSON.stringify(nextSource));
            if (!hasDuplicate) {
              aiMessage.sources.push(nextSource);
              renderSources(aiSourcesBox, aiMessage.sources);
            }
          }

          if (payload.done === true) {
            return;
          }

          if (typeof payload.error === 'string') {
            renderAiBubble(aiBubble, payload.error);
            throw new Error(payload.error);
          }
        } catch (error) {
          console.error('Failed to parse SSE event', raw, error);
        }
      }
    }
  } catch (error) {
    renderAiBubble(aiBubble, error instanceof Error ? error.message : 'Error');
  } finally {
    setSendingState(false);
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!sendButton.disabled) {
    sendMessage();
  }
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    if (!sendButton.disabled) {
      sendMessage();
    }
  }
});

getOrCreateThreadId();
appendMessage('ai', '你好，我是 AI Learning Assistant。你可以直接提问。');
