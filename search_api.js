/**
 * MOSNAUKA AI SEARCH — CLIENT API
 *
 * Отправляет запрос на Flask-бэкенд (mosnauka-backend на Render),
 * который делает поиск по базе НИОКТР и вызывает Claude через OpenRouter.
 *
 * ЛОКАЛЬНО:  бэкенд на http://localhost:5001
 * ПРОДАКШН:  https://mosnauka-backend.onrender.com
 */

// ─── Конфиг ──────────────────────────────────────────────────────────────────
const IS_LOCAL = window.location.hostname === 'localhost' ||
                 window.location.protocol === 'file:';

const BACKEND_URL = IS_LOCAL
  ? 'http://localhost:5001'
  : 'https://mosnauka-backendmosnauka.onrender.com';

const API_ENDPOINT = `${BACKEND_URL}/api/ai-search`;
const REQUEST_TIMEOUT_MS = 60000; // 60 сек (Render Free: cold start + загрузка embeddings)

// ─── fetchAIResults ────────────────────────────────────────────────────────────
/**
 * Отправляет запрос на бэкенд и возвращает нормализованный объект результатов.
 * @param {string} userQuery - Текст запроса (от 2 слов до большого ТЗ)
 * @returns {Promise<Object|null>}
 */
async function fetchAIResults(userQuery) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userQuery }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      console.error('Backend error:', response.status, await response.text());
      return _fallbackResponse(userQuery, 'Ошибка сервера. Попробуйте ещё раз.');
    }

    const data = await response.json();

    // Нормализуем ответ под формат, ожидаемый фронтом
    return _normalize(data);

  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      // Render Free — холодный старт ~30 сек, предупреждаем пользователя
      console.warn('Request timeout — Render cold start?');
      return _fallbackResponse(
        userQuery,
        'Сервер просыпается (холодный старт ~30 сек). Попробуйте ещё раз через момент.'
      );
    }

    console.error('AI Search Error:', error);
    return _fallbackResponse(userQuery, 'Нет соединения с сервером.');
  }
}

// ─── Нормализация ответа бэкенда ──────────────────────────────────────────────
/**
 * Приводит ответ Flask-бэкенда к формату, с которым работает ai_search_results.html
 */
function _normalize(data) {
  const stats = data.stats || {};

  return {
    // ── AI-анализ ──
    ai_summary: data.ai_summary || '',

    // ── Бизнес-метрики (для KPI-блока) ──
    stats: {
      projects_count:  stats.projects_count  || 0,
      rids_count:      stats.rids_count      || 0,
      orgs_count:      stats.orgs_count      || 0,
      total_funding:   _formatRub(stats.total_funding_rub || 0),
      max_match_pct:   stats.max_match_pct   || 0,
    },

    // ── Проекты (топ-3) ──
    projects: (data.projects || []).map(p => ({
      title:           p.title        || '',
      match_percentage: p.match_percentage || 0,
      tags:            p.tags         || [],
      abstract_short:  p.abstract_short || '',
      reg_number:      p.reg_number   || '',
      report_type:     p.report_type  || '',
      budget_rub:      p.budget_rub   || 0,
      year:            p.year         || '',
      org_name:        p.org_name     || '',
      org_slug:        p.org_slug     || '',
      org_logo:        p.org_logo     || '',
    })),

    // ── Организации (топ-3) ──
    organizations: (data.organizations || []).map(o => ({
      org_name:         o.org_name      || '',
      org_name_full:    o.org_name_full || '',
      logo:             o.logo          || '',
      website:          o.website       || '',
      slug:             o.slug          || '',
      projects_count:   o.projects_count   || 0,
      matched_projects: o.matched_projects || 0,
      matched_rids:     o.matched_rids     || 0,
      relevance_score:  o.relevance_score  || 0,
    })),

    // ── Эксперты (топ-3) ──
    experts: (data.experts || []).map(e => ({
      name:      e.name      || '',
      areas:     e.areas     || '',
      org_name:  e.org_name  || '',
      org_logo:  e.org_logo  || '',
      photo:     e.photo     || '',
      colab_url: e.colab_url || '',
    })),

    // ── Квалификация льготы ×2 (Перечень №988) ──
    tax_qualification: data.tax_qualification || null,

    // Отладка (для dev tools)
    _debug: data._debug || {},
  };
}

// ─── Fallback при ошибке ──────────────────────────────────────────────────────
function _fallbackResponse(query, message) {
  return {
    ai_summary: message,
    stats: { projects_count: 0, rids_count: 0, orgs_count: 0, total_funding: '–', max_match_pct: 0 },
    projects: [],
    organizations: [],
    experts: [],
    _error: true,
  };
}

// ─── Утилита форматирования рублей ───────────────────────────────────────────
function _formatRub(amount) {
  if (!amount) return '–';
  if (amount >= 1e9) return `₽${(amount / 1e9).toFixed(1)} млрд`;
  if (amount >= 1e6) return `₽${(amount / 1e6).toFixed(0)} млн`;
  if (amount >= 1e3) return `₽${(amount / 1e3).toFixed(0)} тыс.`;
  return `₽${amount}`;
}
