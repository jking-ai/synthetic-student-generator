import { onRequest } from 'firebase-functions/v2/https';
import { defineString } from 'firebase-functions/params';
import express from 'express';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';
import type { ClientRequest, IncomingMessage } from 'http';

const apiTarget = defineString('API_TARGET');

let app: express.Express | null = null;

function getApp(): express.Express {
  if (app) return app;
  app = express();
  app.use(cors({ origin: true }));
  app.use(
    '/',
    createProxyMiddleware({
      target: apiTarget.value(),
      changeOrigin: true,
      timeout: 300_000,
      on: {
        proxyReq: (proxyReq: ClientRequest, req: IncomingMessage) => {
          const firebaseReq = req as IncomingMessage & { rawBody?: Buffer };
          if (firebaseReq.rawBody?.length) {
            proxyReq.setHeader('Content-Length', firebaseReq.rawBody.length);
            proxyReq.write(firebaseReq.rawBody);
          }
        }
      }
    })
  );
  return app;
}

export const apiProxy = onRequest(
  {
    region: 'us-central1',
    timeoutSeconds: 300,
    memory: '512MiB'
  },
  (req, res) => getApp()(req, res)
);
