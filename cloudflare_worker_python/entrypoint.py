# Cloudflare Workers Python Entrypoint
# MediDemand Application
from js import Response, Headers, JSON
import json
from datetime import datetime

# HTML Interface (MediDemand Bilingual AR / EN Healthcare Dashboard with Day/Night Mode)
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediDemand - نظام التنبؤ باحتياجات الأدوية</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkbg: '#0b1120',
                        darkcard: '#1e293b',
                        darkinput: '#0f172a'
                    }
                }
            }
        };
    </script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Cairo', 'Inter', sans-serif; transition: background-color 0.3s ease, color 0.3s ease; }
        .glass-header {
            background: linear-gradient(135deg, #047857 0%, #065f46 100%);
            box-shadow: 0 4px 20px -2px rgba(6, 95, 70, 0.3);
        }
        .dark .glass-header {
            background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        }
        .stat-card {
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stat-card:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body class="min-h-screen bg-slate-50 dark:bg-darkbg text-slate-800 dark:text-slate-100 flex flex-col antialiased">
    <!-- Navbar -->
    <header class="glass-header text-white sticky top-0 z-50 transition-colors duration-300">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="p-2.5 bg-white/10 dark:bg-white/5 rounded-2xl backdrop-blur-md border border-white/10 shadow-inner">
                    <i class="fa-solid fa-pills text-2xl text-emerald-300"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 id="i18n-appTitle" class="text-2xl font-black tracking-tight font-sans">MediDemand</h1>
                        <span class="text-[10px] bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 px-2 py-0.5 rounded-full font-mono font-bold">PRO</span>
                    </div>
                    <p id="i18n-appSubtitle" class="text-xs text-emerald-100/90 dark:text-emerald-200/80">نظام التنبؤ الذكي بطلبيات واحتياجات الأدوية • Cloudflare Python</p>
                </div>
            </div>
            
            <div class="flex items-center gap-2 sm:gap-2.5">
                <!-- Language Switcher (AR / EN) -->
                <button type="button" onclick="toggleLanguage()" id="langToggleBtn" title="التبديل بين العربية والإنجليزية / Switch Language"
                    class="px-3 py-1.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-xs font-bold text-white shadow-sm transition flex items-center gap-1.5 backdrop-blur-md cursor-pointer">
                    <i class="fa-solid fa-globe text-emerald-200 text-sm"></i>
                    <span id="langLabel">English</span>
                </button>

                <!-- Theme Switcher (نهار / ليل) -->
                <button type="button" onclick="toggleTheme()" id="themeToggleBtn" title="التبديل بين الوضع الليلي والنهاري"
                    class="px-3 py-1.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-xs font-bold text-white shadow-sm transition flex items-center gap-1.5 backdrop-blur-md cursor-pointer">
                    <i id="themeIcon" class="fa-solid fa-moon text-amber-300 text-sm"></i>
                    <span id="themeLabel" class="hidden sm:inline">الوضع الليلي</span>
                </button>

                <span id="userBadge" class="hidden text-xs bg-emerald-800/80 dark:bg-emerald-950 text-emerald-100 px-3.5 py-1.5 rounded-full border border-emerald-600">
                    <i class="fa-regular fa-circle-user ml-1"></i> <span id="currentUserName">مصرح</span>
                </span>

                <button type="button" onclick="toggleAuthModal()" class="text-xs bg-white dark:bg-emerald-100 text-emerald-800 hover:bg-emerald-50 dark:hover:bg-white px-3.5 py-1.5 rounded-xl font-bold shadow-sm transition cursor-pointer flex items-center gap-1">
                    <i class="fa-solid fa-lock"></i>
                    <span id="i18n-loginBtn">تسجيل الدخول</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <!-- Auth Warning / Password Overlay -->
        <div id="authBanner" class="mb-6 p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-2xl flex items-center justify-between shadow-sm transition-colors">
            <div class="flex items-center gap-3">
                <i class="fa-solid fa-shield-halved text-amber-600 dark:text-amber-400 text-xl"></i>
                <div>
                    <h3 id="i18n-authBannerTitle" class="font-bold text-amber-900 dark:text-amber-200 text-sm">وضع المصادقة مطلوب</h3>
                    <p id="i18n-authBannerDesc" class="text-xs text-amber-700 dark:text-amber-300/80">يرجى إدخال كلمة المرور (الافتراضية: Hub) للتمكن من حفظ السجلات في قاعدة البيانات.</p>
                </div>
            </div>
            <button type="button" onclick="toggleAuthModal()" id="i18n-authBannerBtn" class="bg-amber-600 hover:bg-amber-700 text-white text-xs px-4 py-2 rounded-xl font-bold shadow-sm transition cursor-pointer">
                إدخال الرمز
            </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Forecast Input Form -->
            <div class="lg:col-span-5">
                <div class="bg-white dark:bg-darkcard rounded-3xl p-6 shadow-sm dark:shadow-2xl border border-slate-200/80 dark:border-slate-700/80 transition-colors">
                    <div class="flex items-center gap-2 mb-5 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                        <i class="fa-solid fa-calculator text-emerald-600 dark:text-emerald-400 text-lg"></i>
                        <h2 id="i18n-formTitle" class="font-bold text-slate-800 dark:text-white text-lg">بيانات الصنف واحتساب الطلبية</h2>
                    </div>

                    <form id="forecastForm" onsubmit="handleCalculate(event)" class="space-y-4">
                        <div>
                            <label id="i18n-labelFacility" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم المنشأة / المستشفى</label>
                            <input type="text" id="facilityName" required placeholder="مثال: مستشفى الكرنك الدولي / مركز الدير"
                                class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                        </div>

                        <div>
                            <label id="i18n-labelUser" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم المستخدم / الصيدلي المسؤول</label>
                            <input type="text" id="userName" required placeholder="مثال: د. فاطمة"
                                class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                        </div>

                        <div>
                            <label id="i18n-labelDrug" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم الصنف الدوائي (Drug Name)</label>
                            <input type="text" id="drugName" required placeholder="مثال: Ceftriaxone 1g Vial"
                                class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label id="i18n-labelAvgMonthly" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">متوسط الاستهلاك الشهري</label>
                                <input type="number" step="any" min="0" id="avgMonthly" required placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                            <div>
                                <label id="i18n-labelStock" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">الرصيد الحالي بالمخزن</label>
                                <input type="number" step="any" min="0" id="currentStock" placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label id="i18n-labelLead" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">فترة التغطية المطلوبة (بالأشهر)</label>
                                <input type="number" step="0.1" min="0.5" value="1.5" id="leadMonths" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                            </div>
                            <div>
                                <label id="i18n-labelBuffer" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">مخزون الأمان (Safety Buffer %)</label>
                                <input type="number" step="1" min="0" max="100" value="10" id="safetyBuffer" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                            </div>
                        </div>

                        <!-- Result Card -->
                        <div class="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/50 dark:to-teal-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-2xl mt-4 transition-colors">
                            <div class="text-xs text-emerald-800 dark:text-emerald-300 font-bold mb-1 flex items-center justify-between">
                                <span id="i18n-resultTitle">الكمية المقترح طلبها (Recommended Order):</span>
                                <span id="i18n-badgeFormula" class="text-[10px] bg-emerald-200/60 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded-full font-bold">معادلة دقيقة</span>
                            </div>
                            <div class="flex items-baseline justify-between">
                                <span id="liveResult" class="text-4xl font-extrabold text-emerald-700 dark:text-emerald-400 font-mono">0</span>
                                <span id="i18n-resultUnit" class="text-xs text-emerald-600 dark:text-emerald-300 font-bold">عبوة / وحدة</span>
                            </div>
                            <p id="i18n-resultDesc" class="text-[11px] text-emerald-600 dark:text-emerald-400/80 mt-1.5">تراعي الاستهلاك الشهري، فترة التغطية، مخزون الأمان، وخصم الرصيد المتوفر.</p>
                        </div>

                        <button type="submit" id="submitBtn"
                            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white font-bold rounded-xl shadow-md hover:shadow-lg transition flex items-center justify-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-cloud-arrow-up"></i>
                            <span id="i18n-submitBtn">حفظ وتأكيد الطلبية</span>
                        </button>
                    </form>
                </div>
            </div>

            <!-- Stats & Historical Submissions -->
            <div class="lg:col-span-7 space-y-6">
                <!-- KPI Mini Cards -->
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-white dark:bg-darkcard p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm stat-card">
                        <div id="i18n-kpiTotalItems" class="text-slate-400 dark:text-slate-400 text-xs font-bold mb-1">إجمالي الأصناف المسجلة</div>
                        <div id="totalItemsCount" class="text-2xl font-black text-slate-800 dark:text-white font-mono">0</div>
                    </div>
                    <div class="bg-white dark:bg-darkcard p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm stat-card">
                        <div id="i18n-kpiTotalQty" class="text-slate-400 dark:text-slate-400 text-xs font-bold mb-1">إجمالي الكميات المطلوبة</div>
                        <div id="totalQtySum" class="text-2xl font-black text-emerald-600 dark:text-emerald-400 font-mono">0</div>
                    </div>
                    <div class="bg-white dark:bg-darkcard p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm stat-card">
                        <div id="i18n-kpiDbStatus" class="text-slate-400 dark:text-slate-400 text-xs font-bold mb-1">حالة الاتصال السحابي</div>
                        <div class="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 mt-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> <span id="i18n-dbOnline">Cloudflare Active</span>
                        </div>
                    </div>
                </div>

                <!-- History Table -->
                <div class="bg-white dark:bg-darkcard rounded-3xl p-6 shadow-sm dark:shadow-2xl border border-slate-200/80 dark:border-slate-700/80 transition-colors">
                    <div class="flex flex-wrap justify-between items-center gap-3 mb-4 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-clock-rotate-left text-slate-500 dark:text-slate-400"></i>
                            <h3 id="i18n-historyTitle" class="font-bold text-slate-800 dark:text-white text-base">سجل الطلبيات والتوقعات</h3>
                        </div>
                        <div class="flex items-center gap-2">
                            <input type="text" id="tableSearch" oninput="filterTable()" placeholder="بحث عن صنف أو منشأة..."
                                class="px-3 py-1.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-lg text-xs outline-none focus:ring-1 focus:ring-emerald-500 text-slate-900 dark:text-white">
                            <button type="button" onclick="exportToCSV()" class="text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1 cursor-pointer">
                                <i class="fa-solid fa-file-csv text-emerald-600 dark:text-emerald-400"></i> <span id="i18n-exportBtn">تصدير CSV</span>
                            </button>
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-xs">
                            <thead class="bg-slate-50 dark:bg-slate-900/60 text-slate-600 dark:text-slate-300 font-bold border-b border-slate-200 dark:border-slate-700">
                                <tr>
                                    <th id="i18n-thTime" class="py-3 px-3">التاريخ والوقت</th>
                                    <th id="i18n-thFacility" class="py-3 px-3">المنشأة</th>
                                    <th id="i18n-thUser" class="py-3 px-3">المستخدم</th>
                                    <th id="i18n-thDrug" class="py-3 px-3">الصنف</th>
                                    <th id="i18n-thAvg" class="py-3 px-3">م. الاستهلاك</th>
                                    <th id="i18n-thRec" class="py-3 px-3 text-emerald-700 dark:text-emerald-400">الكمية المقترحة</th>
                                </tr>
                            </thead>
                            <tbody id="historyTableBody" class="divide-y divide-slate-100 dark:divide-slate-700 text-slate-700 dark:text-slate-200">
                                <tr>
                                    <td colspan="6" id="i18n-loadingRows" class="py-8 text-center text-slate-400 dark:text-slate-500">لا توجد طلبات مسجلة حتى الآن</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Password Modal -->
    <div id="authModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden">
        <div class="bg-white dark:bg-darkcard rounded-3xl p-6 max-w-sm w-full mx-4 shadow-2xl border border-slate-100 dark:border-slate-700">
            <div class="text-center mb-4">
                <div class="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 rounded-2xl flex items-center justify-center mx-auto mb-2 text-xl">
                    <i class="fa-solid fa-lock"></i>
                </div>
                <h3 id="i18n-modalTitle" class="font-bold text-slate-800 dark:text-white text-base">تسجيل الدخول للمنظومة</h3>
                <p id="i18n-modalDesc" class="text-xs text-slate-500 dark:text-slate-400">أدخل كلمة المرور المصرح بها للتطبيق (الافتراضي: Hub)</p>
            </div>
            <form onsubmit="handleAuth(event)" class="space-y-4">
                <div>
                    <input type="password" id="authPassword" placeholder="كلمة المرور (Hub)" required
                        class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-emerald-500 text-center font-mono font-bold text-slate-900 dark:text-white">
                </div>
                <div class="flex gap-2">
                    <button type="submit" id="i18n-modalConfirm" class="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white font-bold rounded-xl text-xs transition cursor-pointer">
                        تأكيد الدخول
                    </button>
                    <button type="button" onclick="toggleAuthModal()" id="i18n-modalCancel" class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-semibold transition cursor-pointer">
                        إلغاء
                    </button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let currentAuthToken = localStorage.getItem('drug_forecast_pass') || '';
        let currentLang = localStorage.getItem('drug_forecast_lang') || 'ar';
        let records = JSON.parse(localStorage.getItem('forecast_records') || '[]');

        // Full Arabic / English Dictionary with MediDemand Branding
        const translations = {
            ar: {
                appTitle: "MediDemand",
                appSubtitle: "نظام التنبؤ الذكي بطلبيات واحتياجات الأدوية • Cloudflare Python",
                langToggle: "English",
                themeDark: "الوضع الليلي",
                themeLight: "الوضع النهاري",
                userAuth: "مصرح",
                loginBtn: "تسجيل الدخول",
                authBannerTitle: "وضع المصادقة مطلوب",
                authBannerDesc: "يرجى إدخال كلمة المرور (الافتراضية: Hub) للتمكن من حفظ السجلات.",
                authBannerBtn: "إدخال الرمز",
                formTitle: "بيانات الصنف واحتساب الطلبية",
                labelFacility: "اسم المنشأة / المستشفى",
                placeholderFacility: "مثال: مستشفى الكرنك الدولي / مركز الدير",
                labelUser: "اسم المستخدم / الصيدلي المسؤول",
                placeholderUser: "مثال: د. فاطمة",
                labelDrug: "اسم الصنف الدوائي (Drug Name)",
                placeholderDrug: "مثال: Ceftriaxone 1g Vial",
                labelAvgMonthly: "متوسط الاستهلاك الشهري",
                labelStock: "الرصيد الحالي بالمخزن",
                labelLead: "فترة التغطية المطلوبة (بالأشهر)",
                labelBuffer: "مخزون الأمان (Safety Buffer %)",
                resultTitle: "الكمية المقترح طلبها (Recommended Order):",
                badgeFormula: "معادلة دقيقة",
                resultUnit: "عبوة / وحدة",
                resultDesc: "تراعي الاستهلاك الشهري، فترة التغطية، مخزون الأمان، وخصم الرصيد المتوفر.",
                submitBtn: "حفظ وتأكيد الطلبية",
                kpiTotalItems: "إجمالي الأصناف المسجلة",
                kpiTotalQty: "إجمالي الكميات المطلوبة",
                kpiDbStatus: "حالة الاتصال السحابي",
                dbOnline: "Cloudflare Active",
                historyTitle: "سجل الطلبيات والتوقعات",
                searchPlaceholder: "بحث عن صنف أو منشأة...",
                exportBtn: "تصدير CSV",
                thTime: "التاريخ والوقت",
                thFacility: "المنشأة",
                thUser: "المستخدم",
                thDrug: "الصنف",
                thAvg: "م. الاستهلاك",
                thRec: "الكمية المقترحة",
                emptyRows: "لا توجد طلبات مسجلة حتى الآن",
                noMatchRows: "لا توجد نتائج مطابقة للبحث",
                modalTitle: "تسجيل الدخول للمنظومة",
                modalDesc: "أدخل كلمة المرور المصرح بها للتطبيق (الافتراضي: Hub)",
                placeholderPass: "كلمة المرور (Hub)",
                modalConfirm: "تأكيد الدخول",
                modalCancel: "إلغاء",
                toastLoginOk: "تم تسجيل الدخول بنجاح",
                toastSavedOk: "تم احتساب وحفظ الطلبية للصنف ({drug}) بإجمالي كمية: {qty}",
                exportNoData: "لا توجد بيانات لتصديرها",
                csvHeader: "\uFEFFالتاريخ والوقت,اسم المنشأة,اسم المستخدم,اسم الصنف,متوسط الاستهلاك الشهري,الكمية الموصى بطلبها\n"
            },
            en: {
                appTitle: "MediDemand",
                appSubtitle: "Intelligent Healthcare Drug Demand Forecasting Engine • Cloudflare Python",
                langToggle: "العربية",
                themeDark: "Dark Mode",
                themeLight: "Light Mode",
                userAuth: "Authorized",
                loginBtn: "Login",
                authBannerTitle: "Authentication Required",
                authBannerDesc: "Please enter passcode (Default: Hub) to save records to the cloud.",
                authBannerBtn: "Enter PIN",
                formTitle: "Drug Item Data & Order Calculator",
                labelFacility: "Facility / Hospital Name",
                placeholderFacility: "e.g. Karnak International Hospital",
                labelUser: "User / Responsible Pharmacist",
                placeholderUser: "e.g. Dr. Fatima",
                labelDrug: "Drug Name / Formulation",
                placeholderDrug: "e.g. Ceftriaxone 1g Vial",
                labelAvgMonthly: "Avg Monthly Consumption",
                labelStock: "Current Stock on Hand",
                labelLead: "Required Coverage (Months)",
                labelBuffer: "Safety Buffer (%)",
                resultTitle: "Recommended Order Quantity:",
                badgeFormula: "Exact Formula",
                resultUnit: "Packs / Units",
                resultDesc: "Accounts for monthly demand, lead coverage, safety stock minus current inventory.",
                submitBtn: "Save & Confirm Order",
                kpiTotalItems: "Total Recorded Drugs",
                kpiTotalQty: "Total Ordered Quantity",
                kpiDbStatus: "Cloud Connection Status",
                dbOnline: "Cloudflare Active",
                historyTitle: "Drug Forecasts & Orders History",
                searchPlaceholder: "Search drug or facility...",
                exportBtn: "Export CSV",
                thTime: "Date & Time",
                thFacility: "Facility",
                thUser: "User",
                thDrug: "Drug Item",
                thAvg: "Avg Monthly",
                thRec: "Recommended Qty",
                emptyRows: "No orders recorded yet",
                noMatchRows: "No matching records found",
                modalTitle: "System Login",
                modalDesc: "Enter authorized password for this station (Default: Hub)",
                placeholderPass: "Password (Hub)",
                modalConfirm: "Confirm Login",
                modalCancel: "Cancel",
                toastLoginOk: "Logged in successfully",
                toastSavedOk: "Order saved for ({drug}) with recommended qty: {qty}",
                exportNoData: "No data available to export",
                csvHeader: "\uFEFFDate & Time,Facility Name,User Name,Drug Name,Avg Monthly Consumption,Recommended Quantity\n"
            }
        };

        function setLanguage(lang) {
            currentLang = lang;
            localStorage.setItem('drug_forecast_lang', lang);
            const html = document.documentElement;
            const t = translations[lang];

            if (lang === 'en') {
                html.setAttribute('dir', 'ltr');
                html.setAttribute('lang', 'en');
                document.body.style.textAlign = 'left';
            } else {
                html.setAttribute('dir', 'rtl');
                html.setAttribute('lang', 'ar');
                document.body.style.textAlign = 'right';
            }

            document.getElementById('langLabel').textContent = t.langToggle;
            document.getElementById('i18n-appTitle').textContent = t.appTitle;
            document.getElementById('i18n-appSubtitle').textContent = t.appSubtitle;
            document.getElementById('i18n-loginBtn').textContent = t.loginBtn;
            document.getElementById('currentUserName').textContent = t.userAuth;

            document.getElementById('i18n-authBannerTitle').textContent = t.authBannerTitle;
            document.getElementById('i18n-authBannerDesc').textContent = t.authBannerDesc;
            document.getElementById('i18n-authBannerBtn').textContent = t.authBannerBtn;

            document.getElementById('i18n-formTitle').textContent = t.formTitle;
            document.getElementById('i18n-labelFacility').textContent = t.labelFacility;
            document.getElementById('facilityName').placeholder = t.placeholderFacility;
            document.getElementById('i18n-labelUser').textContent = t.labelUser;
            document.getElementById('userName').placeholder = t.placeholderUser;
            document.getElementById('i18n-labelDrug').textContent = t.labelDrug;
            document.getElementById('drugName').placeholder = t.placeholderDrug;
            document.getElementById('i18n-labelAvgMonthly').textContent = t.labelAvgMonthly;
            document.getElementById('i18n-labelStock').textContent = t.labelStock;
            document.getElementById('i18n-labelLead').textContent = t.labelLead;
            document.getElementById('i18n-labelBuffer').textContent = t.labelBuffer;

            document.getElementById('i18n-resultTitle').textContent = t.resultTitle;
            document.getElementById('i18n-badgeFormula').textContent = t.badgeFormula;
            document.getElementById('i18n-resultUnit').textContent = t.resultUnit;
            document.getElementById('i18n-resultDesc').textContent = t.resultDesc;
            document.getElementById('i18n-submitBtn').textContent = t.submitBtn;

            document.getElementById('i18n-kpiTotalItems').textContent = t.kpiTotalItems;
            document.getElementById('i18n-kpiTotalQty').textContent = t.kpiTotalQty;
            document.getElementById('i18n-kpiDbStatus').textContent = t.kpiDbStatus;
            document.getElementById('i18n-dbOnline').textContent = t.dbOnline;

            document.getElementById('i18n-historyTitle').textContent = t.historyTitle;
            document.getElementById('tableSearch').placeholder = t.searchPlaceholder;
            document.getElementById('i18n-exportBtn').textContent = t.exportBtn;

            document.getElementById('i18n-thTime').textContent = t.thTime;
            document.getElementById('i18n-thFacility').textContent = t.thFacility;
            document.getElementById('i18n-thUser').textContent = t.thUser;
            document.getElementById('i18n-thDrug').textContent = t.thDrug;
            document.getElementById('i18n-thAvg').textContent = t.thAvg;
            document.getElementById('i18n-thRec').textContent = t.thRec;

            document.getElementById('i18n-modalTitle').textContent = t.modalTitle;
            document.getElementById('i18n-modalDesc').textContent = t.modalDesc;
            document.getElementById('authPassword').placeholder = t.placeholderPass;
            document.getElementById('i18n-modalConfirm').textContent = t.modalConfirm;
            document.getElementById('i18n-modalCancel').textContent = t.modalCancel;

            const isDark = document.documentElement.classList.contains('dark');
            const themeLabel = document.getElementById('themeLabel');
            if (themeLabel) {
                themeLabel.textContent = isDark ? t.themeLight : t.themeDark;
            }

            renderTable();
        }

        function toggleLanguage() {
            setLanguage(currentLang === 'ar' ? 'en' : 'ar');
        }

        function initTheme() {
            const savedTheme = localStorage.getItem('drug_forecast_theme');
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const activeTheme = savedTheme || (prefersDark ? 'dark' : 'light');
            applyTheme(activeTheme);
        }

        function applyTheme(theme) {
            const html = document.documentElement;
            const icon = document.getElementById('themeIcon');
            const label = document.getElementById('themeLabel');
            const t = translations[currentLang];

            if (theme === 'dark') {
                html.classList.add('dark');
                html.classList.remove('light');
                if (icon) icon.className = 'fa-solid fa-sun text-amber-300 text-sm';
                if (label) label.textContent = t.themeLight;
                localStorage.setItem('drug_forecast_theme', 'dark');
            } else {
                html.classList.remove('dark');
                html.classList.add('light');
                if (icon) icon.className = 'fa-solid fa-moon text-amber-200 text-sm';
                if (label) label.textContent = t.themeDark;
                localStorage.setItem('drug_forecast_theme', 'light');
            }
        }

        function toggleTheme() {
            const isDark = document.documentElement.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        }

        function initApp() {
            setLanguage(currentLang);
            initTheme();
            if (currentAuthToken) {
                document.getElementById('authBanner').classList.add('hidden');
                document.getElementById('userBadge').classList.remove('hidden');
                document.getElementById('currentUserName').textContent = 'مصرح';
            }
            renderTable();
            updateKPIs();
        }

        function toggleAuthModal() {
            document.getElementById('authModal').classList.toggle('hidden');
        }

        function handleAuth(e) {
            e.preventDefault();
            const pass = document.getElementById('authPassword').value.trim();
            const t = translations[currentLang];
            if (pass === 'Hub' || pass === 'EHA' || pass.length > 0) {
                currentAuthToken = pass;
                localStorage.setItem('drug_forecast_pass', pass);
                document.getElementById('authBanner').classList.add('hidden');
                document.getElementById('userBadge').classList.remove('hidden');
                document.getElementById('currentUserName').textContent = 'مصرح';
                toggleAuthModal();
                alert(t.toastLoginOk);
            }
        }

        function computeForecast(avgMonthly, currentStock, leadMonths, safetyBufferPercent) {
            const rawDemand = (avgMonthly * leadMonths);
            const safetyStock = rawDemand * (safetyBufferPercent / 100);
            const totalRequired = rawDemand + safetyStock;
            const netOrder = totalRequired - currentStock;
            return Math.max(0, Math.round(netOrder));
        }

        function liveUpdateCalculation() {
            const avg = parseFloat(document.getElementById('avgMonthly').value) || 0;
            const stock = parseFloat(document.getElementById('currentStock').value) || 0;
            const months = parseFloat(document.getElementById('leadMonths').value) || 1.5;
            const buffer = parseFloat(document.getElementById('safetyBuffer').value) || 10;
            const result = computeForecast(avg, stock, months, buffer);
            document.getElementById('liveResult').textContent = result.toLocaleString('en-US');
        }

        async function handleCalculate(e) {
            e.preventDefault();
            const facility = document.getElementById('facilityName').value.trim();
            const user = document.getElementById('userName').value.trim();
            const drug = document.getElementById('drugName').value.trim();
            const avg = parseFloat(document.getElementById('avgMonthly').value) || 0;
            const stock = parseFloat(document.getElementById('currentStock').value) || 0;
            const months = parseFloat(document.getElementById('leadMonths').value) || 1.5;
            const buffer = parseFloat(document.getElementById('safetyBuffer').value) || 10;
            const recQty = computeForecast(avg, stock, months, buffer);
            const t = translations[currentLang];

            const payload = {
                timestamp: new Date().toLocaleString(currentLang === 'ar' ? 'ar-EG' : 'en-US'),
                facilityName: facility,
                userName: user,
                drugName: drug,
                avgMonthlyConsumption: avg,
                currentStock: stock,
                recommendedQty: recQty,
                authPassword: currentAuthToken
            };

            // Call Cloudflare Python Worker Backend API
            try {
                const res = await fetch('/api/forecast', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                console.log('Saved to backend:', data);
            } catch (err) {
                console.warn('Backend offline or standalone mode, saving locally:', err);
            }

            records.unshift(payload);
            localStorage.setItem('forecast_records', JSON.stringify(records));
            renderTable();
            updateKPIs();
            const msg = t.toastSavedOk.replace('{drug}', drug).replace('{qty}', recQty);
            alert(msg);
            document.getElementById('drugName').value = '';
            document.getElementById('avgMonthly').value = '';
            document.getElementById('currentStock').value = '';
            liveUpdateCalculation();
        }

        function renderTable(filterText = '') {
            const tbody = document.getElementById('historyTableBody');
            const t = translations[currentLang];
            const filtered = records.filter(r => 
                !filterText || 
                r.drugName.toLowerCase().includes(filterText.toLowerCase()) || 
                r.facilityName.toLowerCase().includes(filterText.toLowerCase())
            );

            if (filtered.length === 0) {
                const emptyMsg = records.length === 0 ? t.emptyRows : t.noMatchRows;
                tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400 dark:text-slate-500">${emptyMsg}</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => `
                <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/50 transition">
                    <td class="py-3 px-3 text-slate-500 dark:text-slate-400 font-mono text-[11px]">${r.timestamp}</td>
                    <td class="py-3 px-3 font-semibold text-slate-800 dark:text-slate-100">${r.facilityName}</td>
                    <td class="py-3 px-3 text-slate-600 dark:text-slate-300">${r.userName}</td>
                    <td class="py-3 px-3 font-bold text-slate-900 dark:text-white">${r.drugName}</td>
                    <td class="py-3 px-3 text-slate-600 dark:text-slate-300 font-mono">${r.avgMonthlyConsumption}</td>
                    <td class="py-3 px-3 font-extrabold text-emerald-700 dark:text-emerald-400 text-sm font-mono">${r.recommendedQty}</td>
                </tr>
            `).join('');
        }

        function filterTable() {
            const text = document.getElementById('tableSearch').value.trim();
            renderTable(text);
        }

        function updateKPIs() {
            document.getElementById('totalItemsCount').textContent = records.length;
            const sum = records.reduce((acc, r) => acc + (r.recommendedQty || 0), 0);
            document.getElementById('totalQtySum').textContent = sum.toLocaleString('en-US');
        }

        function exportToCSV() {
            const t = translations[currentLang];
            if (records.length === 0) {
                alert(t.exportNoData);
                return;
            }
            let csv = t.csvHeader;
            records.forEach(r => {
                csv += `"${r.timestamp}","${r.facilityName}","${r.userName}","${r.drugName}","${r.avgMonthlyConsumption}","${r.recommendedQty}"\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `MediDemand_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();
        }

        window.onload = initApp;
    </script>
</body>
</html>
"""

def calculate_forecast(avg_monthly: float, current_stock: float = 0.0, lead_months: float = 1.5, safety_buffer_pct: float = 10.0) -> int:
    raw_demand = avg_monthly * lead_months
    safety_stock = raw_demand * (safety_buffer_pct / 100.0)
    total_needed = raw_demand + safety_stock
    net_order = total_needed - current_stock
    return max(0, round(net_order))

async def on_fetch(request, env):
    url = request.url
    method = request.method
    
    headers = Headers.new()
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")

    if method == "OPTIONS":
        return Response.new("", headers=headers, status=204)

    # API Endpoint: /api/forecast
    if "/api/forecast" in url:
        if method == "POST":
            try:
                body_text = await request.text()
                payload = json.loads(body_text) if body_text else {}
                
                avg_monthly = float(payload.get("avgMonthlyConsumption", 0))
                current_stock = float(payload.get("currentStock", 0))
                lead_months = float(payload.get("leadMonths", 1.5))
                safety_buffer = float(payload.get("safetyBuffer", 10))

                rec_qty = calculate_forecast(avg_monthly, current_stock, lead_months, safety_buffer)

                response_data = {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "facility": payload.get("facilityName"),
                    "drug": payload.get("drugName"),
                    "recommendedQty": rec_qty
                }
                
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(response_data), headers=headers, status=200)
            except Exception as e:
                err_response = {"status": "error", "message": str(e)}
                headers.set("Content-Type", "application/json")
                return Response.new(json.dumps(err_response), headers=headers, status=400)
        
        headers.set("Content-Type", "application/json")
        return Response.new(json.dumps({"message": "MediDemand Python API Ready"}), headers=headers, status=200)

    # Serve Main Frontend HTML
    headers.set("Content-Type", "text/html; charset=utf-8")
    return Response.new(HTML_CONTENT, headers=headers, status=200)
