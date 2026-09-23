/**
 * OpenRouter AI Integration Module - Resilient Edition
 * Includes automatic retry, rate-limit (429) handling, and fallback logic.
 */

class OpenRouterClient {
    constructor() {
        this.apiKey = localStorage.getItem('OPENROUTER_API_KEY') || 'REDACTED_API_KEY';
        this.selectedModel = localStorage.getItem('OPENROUTER_MODEL') || 'openrouter/free';
        this.baseUrl = 'https://openrouter.ai/api/v1';

        this.fallbackModels = [
            'openrouter/free',
            'nvidia/nemotron-3-ultra-550b:free',
            'google/gemma-4-31b-it:free',
            'nvidia/nemotron-3-nano-30b:free',
            'openai/gpt-oss-20b:free',
            'dots3-note:free'
        ];
    }

    setApiKey(key) {
        this.apiKey = key;
        localStorage.setItem('OPENROUTER_API_KEY', key);
    }

    setModel(model) {
        this.selectedModel = model;
        localStorage.setItem('OPENROUTER_MODEL', model);
    }

    async getFreeModels() {
        try {
            const response = await fetch(`${this.baseUrl}/models`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            const freeModels = data.data.filter(model => {
                const isFreePricing = model.pricing && (parseFloat(model.pricing.prompt) === 0 && parseFloat(model.pricing.completion) === 0);
                const isFreeId = model.id.endsWith(':free') || model.id === 'openrouter/free';
                return isFreePricing || isFreeId;
            });

            return freeModels.length > 0 ? freeModels : this.getPredefinedFreeModels();
        } catch (err) {
            console.warn('Failed to query live OpenRouter models, using fallback list:', err);
            return this.getPredefinedFreeModels();
        }
    }

    getPredefinedFreeModels() {
        return [
            { id: 'openrouter/free', name: 'OpenRouter Free Auto-Router', description: 'Automatically routes to the best available online free model.' },
            { id: 'nvidia/nemotron-3-ultra-550b:free', name: 'NVIDIA Nemotron 3 Ultra 550B (1M Context)', description: 'Flagship 550B model with 1 Million token context.' },
            { id: 'google/gemma-4-31b-it:free', name: 'Google Gemma 4 31B (262K Context)', description: 'Google premier open weights model for structured code and JSON.' },
            { id: 'nvidia/nemotron-3-nano-30b:free', name: 'NVIDIA Nemotron 3 Nano 30B', description: 'Sub-40ms fast reasoning for real-time agent loops.' },
            { id: 'openai/gpt-oss-20b:free', name: 'OpenAI GPT-OSS 20B (Free)', description: 'Open weights model tuned by OpenAI.' },
            { id: 'dots3-note:free', name: 'Dots3-Note MoE (16B Active)', description: 'High-speed reasoning MoE with low latency.' }
        ];
    }

    async completePrompt(messages, options = {}) {
        const modelsToTry = Array.from(new Set([
            this.selectedModel,
            'openrouter/free',
            ...this.fallbackModels
        ]));

        let lastError = null;

        for (const model of modelsToTry) {
            try {
                const response = await fetch(`${this.baseUrl}/chat/completions`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'HTTP-Referer': window.location.href,
                        'X-Title': 'AutoMonetize AI Studio',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        model: model,
                        messages: messages,
                        temperature: options.temperature || 0.7,
                        max_tokens: options.max_tokens || 2048
                    })
                });

                const data = await response.json().catch(() => null);

                if (!response.ok) {
                    const errMsg = data?.error?.message || response.statusText;
                    throw new Error(`Model ${model} [HTTP ${response.status}]: ${errMsg}`);
                }

                if (data && data.choices && data.choices.length > 0 && data.choices[0].message) {
                    const content = data.choices[0].message.content;
                    if (content) {
                        return {
                            content: content,
                            modelUsed: data.model || model
                        };
                    }
                }
                
                throw new Error(`Model ${model} returned empty choice content.`);
            } catch (err) {
                console.warn(`Attempt with ${model} failed:`, err.message);
                lastError = err;
            }
        }

        throw new Error(`All free model attempts failed or were rate-limited. Last error: ${lastError?.message}`);
    }

    async generateMoneyBlueprint(niche, modelType, complexity, customNotes = '') {
        const systemPrompt = `You are AutoMonetize AI, a world-class venture capitalist and software architect.
Generate a structured, actionable monetization blueprint for the requested app idea.

Format with clear headers:
1. **App Name & Pitch** (Unique brand name and 1-line elevator pitch)
2. **Target Audience & Value Proposition** (Who pays and why)
3. **Monetization Mechanics** (Free Tier, Paid Subscriptions, API Credit Pricing)
4. **Core Technical Architecture** (Frontend, Backend API, Database, Payments)
5. **Growth Strategy & CAC/LTV Estimates**
6. **Projected Monthly Recurring Revenue (MRR)**`;

        const userPrompt = `Target Sector: ${niche}
Monetization Model: ${modelType}
Complexity Level: ${complexity}
Custom Constraints: ${customNotes || 'Leverage free LLMs and modern web stack'}`;

        return await this.completePrompt([
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ]);
    }

    async generateAppCode(appTitle, blueprintText, fileType) {
        const systemPrompt = `You are a principal software engineer. Write high-quality, production-ready source code for file '${fileType}'.
Return ONLY raw source code without conversational backticks or chatter.`;

        const userPrompt = `App Name: ${appTitle}
Blueprint Context: ${blueprintText.substring(0, 1000)}

Please generate file contents for: ${fileType}
- html: Modern glassmorphism HTML structure, CSS links, input controls, and monetization buttons.
- css: Cyber dark theme, variables, card styles, and mobile responsive flex/grid layouts.
- js: Clean ES6 script, interactive state, mock checkout handler, and OpenRouter fetch call.
- py: Python FastAPI code with CORS, Pydantic schemas, and endpoints.
- monetize: Payment Gateway integration snippet for Stripe / LemonSqueezy / Gumroad.`;

        return await this.completePrompt([
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ]);
    }
}

window.openRouterClient = new OpenRouterClient();
