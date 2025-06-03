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

@customElement("ak-flow-source-wecom")
export class WeComLoginInit extends BaseStage<WeComLoginChallenge, WeComChallengeResponseRequest> {
    qrCodeRef = createRef();

    static get styles(): CSSResult[] {
        return [PFBase, PFLogin, PFButton, PFTitle];
    }

    async firstUpdated(): Promise<void> {
        const baseUrl = "https://open.weixin.qq.com/connect/oauth2/authorize";

        const queryParams = new URLSearchParams();
        queryParams.append("appid", this.challenge.corpId);
        queryParams.append("redirect_uri", encodeURIComponent(this.challenge.callbackUri));
        queryParams.append("response_type", "code");
        queryParams.append("scope", "snsapi_privateinfo");
        queryParams.append("state", this.challenge.state);
        queryParams.append("agentid", this.challenge.agentId);

        const authUrl = `${baseUrl}?${queryParams.toString()}#wechat_redirect`;
        console.log(authUrl);

        await QRCode.toCanvas(this.qrCodeRef.value, authUrl, { errorCorrectionLevel: "L" });

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
