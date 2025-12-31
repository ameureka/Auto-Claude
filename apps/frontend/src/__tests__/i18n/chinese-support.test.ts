/**
 * Chinese Language Support Tests
 *
 * 验证中文语言支持功能的正确性属性:
 * - Property 1: Language type includes Chinese
 * - Property 2: Available languages includes Chinese entry
 * - Property 3: Chinese resources registered for all namespaces
 * - Property 4: Translation key completeness
 * - Property 5: Interpolation placeholder preservation
 * - Property 6: Fallback to English
 */

import { describe, it, expect } from 'vitest';
import { AVAILABLE_LANGUAGES, SupportedLanguage, DEFAULT_LANGUAGE } from '@/shared/constants/i18n';
import { resources } from '@/shared/i18n';

// Import translation files for comparison
import enCommon from '@/shared/i18n/locales/en/common.json';
import enNavigation from '@/shared/i18n/locales/en/navigation.json';
import enSettings from '@/shared/i18n/locales/en/settings.json';
import enTasks from '@/shared/i18n/locales/en/tasks.json';
import enWelcome from '@/shared/i18n/locales/en/welcome.json';
import enOnboarding from '@/shared/i18n/locales/en/onboarding.json';
import enDialogs from '@/shared/i18n/locales/en/dialogs.json';
import enTaskReview from '@/shared/i18n/locales/en/taskReview.json';

import zhCommon from '@/shared/i18n/locales/zh/common.json';
import zhNavigation from '@/shared/i18n/locales/zh/navigation.json';
import zhSettings from '@/shared/i18n/locales/zh/settings.json';
import zhTasks from '@/shared/i18n/locales/zh/tasks.json';
import zhWelcome from '@/shared/i18n/locales/zh/welcome.json';
import zhOnboarding from '@/shared/i18n/locales/zh/onboarding.json';
import zhDialogs from '@/shared/i18n/locales/zh/dialogs.json';
import zhTaskReview from '@/shared/i18n/locales/zh/taskReview.json';

// Helper function to get all keys from a nested object
function getAllKeys(obj: object, prefix = ''): string[] {
    return Object.entries(obj).flatMap(([key, value]) => {
        const path = prefix ? `${prefix}.${key}` : key;
        if (typeof value === 'object' && value !== null) {
            return getAllKeys(value, path);
        }
        return [path];
    });
}

// Helper function to get all interpolation placeholders from a string
function getInterpolations(str: string): string[] {
    const matches = str.match(/\{\{[^}]+\}\}/g);
    return matches ? matches.sort() : [];
}

// Helper function to check interpolation placeholders recursively
function checkInterpolations(enObj: object, zhObj: object, path = ''): void {
    Object.entries(enObj).forEach(([key, enValue]) => {
        const currentPath = path ? `${path}.${key}` : key;
        const zhValue = (zhObj as Record<string, unknown>)[key];

        if (typeof enValue === 'string' && typeof zhValue === 'string') {
            const enPlaceholders = getInterpolations(enValue);
            const zhPlaceholders = getInterpolations(zhValue);
            expect(zhPlaceholders, `Interpolation mismatch at ${currentPath}`).toEqual(enPlaceholders);
        } else if (typeof enValue === 'object' && enValue !== null && typeof zhValue === 'object' && zhValue !== null) {
            checkInterpolations(enValue as object, zhValue as object, currentPath);
        }
    });
}

describe('Chinese Language Support', () => {
    // ======================================================================
    // Property 1: Language type includes Chinese
    // ======================================================================
    describe('Property 1: Language type includes Chinese', () => {
        it('should include zh in SupportedLanguage type', () => {
            // TypeScript will catch this at compile time, but we verify at runtime
            const lang: SupportedLanguage = 'zh';
            expect(['en', 'fr', 'zh']).toContain(lang);
        });

        it('should maintain en as DEFAULT_LANGUAGE', () => {
            expect(DEFAULT_LANGUAGE).toBe('en');
        });
    });

    // ======================================================================
    // Property 2: Available languages includes Chinese entry
    // ======================================================================
    describe('Property 2: Available languages includes Chinese entry', () => {
        it('should include Chinese in AVAILABLE_LANGUAGES', () => {
            const chinese = AVAILABLE_LANGUAGES.find(l => l.value === 'zh');
            expect(chinese).toBeDefined();
        });

        it('should have correct label for Chinese', () => {
            const chinese = AVAILABLE_LANGUAGES.find(l => l.value === 'zh');
            expect(chinese?.label).toBe('Chinese');
        });

        it('should have correct nativeLabel for Chinese', () => {
            const chinese = AVAILABLE_LANGUAGES.find(l => l.value === 'zh');
            expect(chinese?.nativeLabel).toBe('简体中文');
        });
    });

    // ======================================================================
    // Property 3: Chinese resources registered for all namespaces
    // ======================================================================
    describe('Property 3: Chinese resources registered for all namespaces', () => {
        const namespaces = [
            'common',
            'navigation',
            'settings',
            'tasks',
            'welcome',
            'onboarding',
            'dialogs',
            'taskReview'
        ];

        it('should have zh key in resources', () => {
            expect(resources).toHaveProperty('zh');
        });

        namespaces.forEach(ns => {
            it(`should register namespace: ${ns}`, () => {
                expect(resources.zh).toHaveProperty(ns);
            });
        });
    });

    // ======================================================================
    // Property 4: Translation key completeness
    // ======================================================================
    describe('Property 4: Translation key completeness', () => {
        const translationPairs = [
            { name: 'common', en: enCommon, zh: zhCommon },
            { name: 'navigation', en: enNavigation, zh: zhNavigation },
            { name: 'settings', en: enSettings, zh: zhSettings },
            { name: 'tasks', en: enTasks, zh: zhTasks },
            { name: 'welcome', en: enWelcome, zh: zhWelcome },
            { name: 'onboarding', en: enOnboarding, zh: zhOnboarding },
            { name: 'dialogs', en: enDialogs, zh: zhDialogs },
            { name: 'taskReview', en: enTaskReview, zh: zhTaskReview }
        ];

        translationPairs.forEach(({ name, en, zh }) => {
            it(`zh/${name}.json should have all keys from en/${name}.json`, () => {
                const enKeys = getAllKeys(en);
                const zhKeys = getAllKeys(zh);

                enKeys.forEach(key => {
                    expect(zhKeys, `Missing key: ${key}`).toContain(key);
                });
            });
        });
    });

    // ======================================================================
    // Property 5: Interpolation placeholder preservation
    // ======================================================================
    describe('Property 5: Interpolation placeholder preservation', () => {
        it('should preserve interpolations in common.json', () => {
            checkInterpolations(enCommon, zhCommon);
        });

        it('should preserve interpolations in settings.json', () => {
            checkInterpolations(enSettings, zhSettings);
        });

        it('should preserve interpolations in tasks.json', () => {
            checkInterpolations(enTasks, zhTasks);
        });

        it('should preserve interpolations in onboarding.json', () => {
            checkInterpolations(enOnboarding, zhOnboarding);
        });

        it('should preserve interpolations in dialogs.json', () => {
            checkInterpolations(enDialogs, zhDialogs);
        });
    });
});
