import * as _zhLocale from "@goauthentik/locales/zh";

import type { LocaleModule } from "@lit/localize";
import { msg } from "@lit/localize";

import { AkLocale, LocaleRow } from "./types";

export const DEFAULT_FALLBACK = "zh";

const zhLocale: LocaleModule = _zhLocale;

export { zhLocale };

// NOTE: This table cannot be made any shorter, despite all the repetition of syntax. Bundlers look
// for the `await import` string as a *string target* for doing alias substitution, so putting
// the import in some sort of abstracting function doesn't work. The same is true for the `msg()`
// function, which `localize` uses to find strings for extraction and translation. Likewise,
// because this is a file-level table, the `msg()` must be thunked so that they're re-run when
// the user changes the locale.

// NOTE: The matchers try to conform loosely to [RFC
// 5646](https://www.rfc-editor.org/rfc/rfc5646.txt), "Tags for the Identification of Languages." In
// practice, language tags have been seen using both hyphens and underscores, and the Chinese
// language uses both "regional" and "script" suffixes. The regexes use the language and any region
// or script.
//
// Chinese locales usually (but not always) use the script rather than region suffix. The default
// (optional) fallback for Chinese (zh) is "Chinese (simplified)", which is why it has that odd
// regex syntax at the end which means "match zh as long as it's not followed by a [:word:] token";
// Traditional script and the Taiwanese are attempted first, and if neither matches, anything
// beginning with that generic "zh" is mapped to "Chinese (simplified)."

// - Code for Lit/Locale
// - Regex for matching user-supplied locale.
// - Text Label
// - Locale loader.

// prettier-ignore
const debug: LocaleRow = [
    "pseudo-LOCALE", /^pseudo/i, () => msg("Pseudolocale (for testing)"), async () => await import("@goauthentik/locales/pseudo-LOCALE"),
];

// prettier-ignore
const LOCALE_TABLE: LocaleRow[] = [
    ["en",      /^en([_-]|$)/i,      () => msg("English"),               async () => await import("@goauthentik/locales/en")],
    ["zh",      /^zh([_-]|$)/i,      () => msg("Chinese (simplified)"),  async () => await import("@goauthentik/locales/zh")],
    debug
];

export const LOCALES: AkLocale[] = LOCALE_TABLE.map(([code, match, label, locale]) => ({
    code,
    match,
    label,
    locale,
}));

export default LOCALES;
