// Realtime — خادم Socket.IO مستقل عن web
// الحالة الفعلية: هيكل يعمل فعليًا (اتصال، انضمام لغرفة محادثة، بث رسالة للغرفة) مع Health check.
// غير مكتمل بعد: التحقق من الجلسة عبر ush_session، حفظ الرسائل في Message، حالة القراءة، منع مشاركة معلومات حساسة.
// هذا جزء من المرحلة 3 (لم تكتمل) — راجع IMPLEMENTATION_PLAN.md. لا تُستخدم هذه النسخة بإنتاج قبل إغلاق هذه الفجوات.

import { createServer } from "node:http";
import { Server } from "socket.io";

const PORT = Number(process.env.REALTIME_PORT ?? 4000);

const httpServer = createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ status: "ok", service: "realtime" }));
    return;
  }
  res.writeHead(404);
  res.end();
});

const io = new Server(httpServer, {
  cors: { origin: process.env.APP_URL ?? "*" },
});

io.on("connection", (socket) => {
  console.log(`[realtime] client connected: ${socket.id}`);

  socket.on("conversation:join", (conversationId: string) => {
    socket.join(`conversation:${conversationId}`);
  });

  socket.on("conversation:message", (payload: { conversationId: string; body: string; senderId: string }) => {
    // TODO: التحقق من صلاحية senderId عبر جلسة موقّعة قبل الإنتاج، وحفظ الرسالة بجدول Message
    io.to(`conversation:${payload.conversationId}`).emit("conversation:message", {
      ...payload,
      createdAt: new Date().toISOString(),
    });
  });

  socket.on("disconnect", () => {
    console.log(`[realtime] client disconnected: ${socket.id}`);
  });
});

httpServer.listen(PORT, () => {
  console.log(`[realtime] listening on :${PORT}`);
});
