import { DEFAULT_CONFIG } from "@goauthentik/common/api/config";
import "@goauthentik/elements/EmptyState";
import { BaseStage } from "@goauthentik/flow/stages/base";
import QRCode from "qrcode";

import { msg } from "@lit/localize";
import { CSSResult, TemplateResult, html } from "lit";
import { customElement } from "lit/decorators.js";
import { createRef, ref } from "lit/directives/ref.js";

import PFButton from "@patternfly/patternfly/components/Button/button.css";
import PFLogin from "@patternfly/patternfly/components/Login/login.css";
import PFTitle from "@patternfly/patternfly/components/Title/title.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";

import {
    ResponseError,
    SourcesApi,
    WeComChallengeResponseRequest,
    WeComLoginChallenge,
} from "@goauthentik/api";

const baseUrl = "https://open.weixin.qq.com/connect/oauth2/authorize";

@customElement("ak-flow-source-wecom")
export class WeComLoginInit extends BaseStage<WeComLoginChallenge, WeComChallengeResponseRequest> {
    qrCodeRef = createRef();

    static get styles(): CSSResult[] {
        return [PFBase, PFLogin, PFButton, PFTitle];
    }

    async mobileLogin(): Promise<void> {
        const queryParams = new URLSearchParams();
        queryParams.append("appid", this.challenge.corpId);
        queryParams.append("redirect_uri", encodeURIComponent(this.challenge.mobileUri));
        queryParams.append("response_type", "code");
        queryParams.append("scope", "snsapi_privateinfo");
        queryParams.append("state", this.challenge.state);
        queryParams.append("agentid", this.challenge.agentId);

        const mobileUrl = `${baseUrl}?${queryParams.toString()}#wechat_redirect`;

        await QRCode.toCanvas(this.qrCodeRef.value, mobileUrl, { errorCorrectionLevel: "L" });

        const interval = setInterval(() => {
            new SourcesApi(DEFAULT_CONFIG)
                .sourcesWecomValidateCodeCreate({
                    weComCodeValidationRequest: {
                        state: this.challenge.state,
                    },
                    slug: this.challenge?.slug || "",
                })
                .then((redirectChallenge) => {
                    window.location.assign(redirectChallenge.to);
                })
                .catch((err: ResponseError) => {
                    if (err.response.status === 400) return;
                    clearInterval(interval);
                    throw err;
                });
        }, 1000);
    }

    callbackLogin(): void {
        const callbackQueryParams = new URLSearchParams();
        callbackQueryParams.append("slug", this.challenge?.slug || "");
        const callbackUrl = `${this.challenge.callbackUri}?${callbackQueryParams.toString()}`;

        const loginQueryParams = new URLSearchParams();
        loginQueryParams.append("appid", this.challenge.corpId);
        loginQueryParams.append("redirect_uri", encodeURIComponent(callbackUrl));
        loginQueryParams.append("response_type", "code");
        loginQueryParams.append("scope", "snsapi_privateinfo");
        loginQueryParams.append("state", this.challenge.state);
        loginQueryParams.append("agentid", this.challenge.agentId);

        const loginUrl = `${baseUrl}?${loginQueryParams.toString()}#wechat_redirect`;
        window.location.assign(loginUrl);
    }

    async firstUpdated(): Promise<void> {
        const ua = window.navigator.userAgent.toLowerCase();
        if (ua.indexOf("wxwork") !== -1 || ua.indexOf("micromessenger") !== -1) {
            this.callbackLogin();
        } else {
            await this.mobileLogin();
        }
    }

    render(): TemplateResult {
        return html` <header class="pf-c-login__main-header">
                <h1 class="pf-c-title pf-m-3xl">${msg("Authenticating with WeCom...")}</h1>
            </header>
            <div class="pf-c-login__main-body" style="display: flex; justify-content: center;">
                <canvas ${ref(this.qrCodeRef)}></canvas>
            </div>
            <footer class="pf-c-login__main-footer">
                <ul class="pf-c-login__main-footer-links"></ul>
            </footer>`;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        "ak-flow-source-wecom": WeComLoginInit;
    }
}
