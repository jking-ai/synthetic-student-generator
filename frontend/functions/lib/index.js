"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.apiProxy = void 0;
const https_1 = require("firebase-functions/v2/https");
const params_1 = require("firebase-functions/params");
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const http_proxy_middleware_1 = require("http-proxy-middleware");
const apiTarget = (0, params_1.defineString)('API_TARGET');
let app = null;
function getApp() {
    if (app)
        return app;
    app = (0, express_1.default)();
    app.use((0, cors_1.default)({ origin: true }));
    app.use('/', (0, http_proxy_middleware_1.createProxyMiddleware)({
        target: apiTarget.value(),
        changeOrigin: true,
        timeout: 300_000,
        on: {
            proxyReq: (proxyReq, req) => {
                const firebaseReq = req;
                if (firebaseReq.rawBody?.length) {
                    proxyReq.setHeader('Content-Length', firebaseReq.rawBody.length);
                    proxyReq.write(firebaseReq.rawBody);
                }
            }
        }
    }));
    return app;
}
exports.apiProxy = (0, https_1.onRequest)({
    region: 'us-central1',
    timeoutSeconds: 300,
    memory: '512MiB'
}, (req, res) => getApp()(req, res));
//# sourceMappingURL=index.js.map