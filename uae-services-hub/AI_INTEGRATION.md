# AI_INTEGRATION

> **لم يُبنَ أي جزء من هذا الملف بعد.** هذا تصميم للمرحلة 5 فقط، موثَّق مسبقًا حتى يكون تنفيذها ميكانيكيًا. لا تعتبر أي كود هنا موجودًا فعليًا بالمشروع.

## المبدأ المضاد للهلوسة (غير قابل للتفاوض)

المساعد **لا يجيب من معرفته العامة** عن أسعار أو شركات أو قوانين إماراتية. القواعد:

1. المساعد لا يملك إلا **أدوات** (function calling): `search_listings`, `search_providers`, `get_price_range`, `search_kb`.
2. صفر نتائج من أداة → رد إجباري: «ما لقيت شي مطابق في المنصة» + اقتراح توسيع البحث. **ممنوع الاختراع.**
3. أي إجابة قانونية/تنظيمية تُرجع مع **المصدر + تاريخ آخر مراجعة** من `KnowledgeArticle.sourceUrl` و`lastReviewedAt`. بدون مصدر موثوق بقاعدة المعرفة → لا إجابة قاطعة، بل توجيه لمصدر رسمي.
4. **طبقة تحقق بعد التوليد**: أي رقم درهم أو اسم شركة بالرد يجب أن يطابق `id` موجود فعليًا بنتائج استدعاءات الأدوات (مقارنة نصية/رقمية آلية على الرد قبل إرساله للمستخدم) — وإلا يُحجب الرد ويُستبدل برسالة "تعذّر التحقق من هذه المعلومة".

## ترتيب مصادر الإجابة

1. بيانات قاعدة بيانات المنصة (`Listing`, `Company` عبر الأدوات).
2. قاعدة المعرفة الداخلية (`KnowledgeArticle` + بحث Qdrant دلالي).
3. أدوات بحث خارجي (إن فُعِّلت مستقبلًا).
4. معرفة عامة **فقط** لمعلومات غير حساسة وغير متغيرة (مثال: "ما معنى GCC Specs؟") — أبدًا لسعر أو اسم شركة أو نص قانوني.

## AI Provider Abstraction (تصميم)

```ts
// lib/ai/provider.ts (غير موجود بعد)
interface AiProvider {
  chat(messages: AiMessage[], tools: ToolDefinition[]): AsyncIterable<AiStreamChunk>;
}
```

مزودون مخطَّطون خلف نفس الواجهة:
- `AnthropicProvider` — Claude API مباشرة
- `OpenAiCompatibleProvider` — أي مزود يدعم OpenAI Chat Completions format
- `OllamaProvider` — محلي، عبر `OLLAMA_BASE_URL`

الاختيار عبر `AI_PROVIDER` بـ `.env` (`.env.example` يحتوي القالب فعلاً). راجع `REQUIRED_USER_INPUT.md` #4 — القرار قرارك.

## RAG (تصميم)

- Qdrant (الخدمة موجودة بـ `docker-compose.yml` فعلاً، غير مستخدمة بعد)
- `KnowledgeArticle.qdrantPointId` موجود بالمخطط فعلاً لربط كل مقال بنقطة Qdrant بعد الفهرسة
- مزود embeddings قابل للتبديل عبر `EMBEDDINGS_PROVIDER`/`EMBEDDINGS_BASE_URL` (`.env.example`)
- خط أنابيب الفهرسة (worker job): مقال جديد/مُعدَّل → تقسيم نصي → embedding → upsert بـ Qdrant → تحديث `qdrantPointId`

## سجل الاستخدام وحدوده

`AiConversation` + `AiMessage` موجودان بالمخطط فعلاً بحقول `toolCalls` (Json) و`citations` (Json) و`tokensUsed` — مصمَّمان تحديدًا لدعم طبقة التحقق في البند 4 أعلاه. لا حدود استخدام (rate limit بالتوكن) مطبَّقة بعد لأن الميزة نفسها غير موجودة.

## الأدوات المخطَّطة (function calling)

| الأداة | تستعلم | ملاحظة |
|---|---|---|
| `search_listings` | `Listing` (status=PUBLISHED) بالفلاتر | تعيد `id, title, price, emirate` فقط — لا نص حر يمكن اختراعه |
| `search_providers` | `Company` (status=ACTIVE) | |
| `get_price_range` | `avg/min/max` على `Listing.price` مجمَّعة بالقسم/الإمارة | |
| `search_kb` | بحث دلالي على `KnowledgeArticle` عبر Qdrant | يعيد `sourceUrl` و`lastReviewedAt` إلزاميًا |
