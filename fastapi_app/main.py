# FastAPI Application for MediDemand
# MAG Healthcare Solutions • Hospital & Primary Care Drug Forecasting Platform
import os
import re
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="MediDemand",
    description="Hospital & Primary Care Healthcare Drug Forecasting Platform - MAG Healthcare Solutions",
    version="5.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

class ForecastInput(BaseModel):
    facility_name: Optional[str] = None
    facilityName: Optional[str] = None
    user_name: Optional[str] = None
    userName: Optional[str] = None
    drug_name: Optional[str] = None
    drugName: Optional[str] = None
    m1_consumption: Optional[float] = 0.0
    m2_consumption: Optional[float] = 0.0
    m3_consumption: Optional[float] = 0.0
    avg_monthly_consumption: Optional[float] = None
    current_stock: Optional[float] = 0.0
    currentStock: Optional[float] = 0.0
    lead_days: Optional[float] = 30.0
    leadDays: Optional[float] = 30.0
    safety_days: Optional[float] = 15.0
    safetyDays: Optional[float] = 15.0

class ForecastOutput(BaseModel):
    status: str
    recommended_qty: int
    avg_monthly: float
    daily_demand: float
    total_days: float
    timestamp: str
    facility: Optional[str] = None
    drug: Optional[str] = None

def calculate_forecast_logic(m1: float, m2: float, m3: float, lead_days: float, safety_days: float, current_stock: float) -> tuple[int, float, float, float]:
    avg_monthly = (m1 + m2 + m3) / 3.0
    daily_demand = avg_monthly / 30.0
    total_days = lead_days + safety_days
    total_needed = daily_demand * total_days
    net_order = total_needed - current_stock
    return max(0, round(net_order)), round(avg_monthly, 2), round(daily_demand, 2), total_days

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediDemand • MAG Healthcare Solutions</title>
    <link rel="icon" type="image/png" href="/logo.png">
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
        .logo-glow {
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));
            transition: transform 0.3s ease;
        }
        .logo-glow:hover {
            transform: scale(1.05);
        }
        .auth-tab-active {
            border-bottom: 2px solid #059669;
            color: #059669;
            font-weight: 700;
        }
        .dark .auth-tab-active {
            border-bottom: 2px solid #34d399;
            color: #34d399;
        }
    </style>
</head>
<body class="min-h-screen bg-slate-50 dark:bg-darkbg text-slate-800 dark:text-slate-100 flex flex-col antialiased">
    <!-- Navbar -->
    <header class="glass-header text-white sticky top-0 z-50 transition-colors duration-300">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
            <!-- Brand & Logo -->
            <div class="flex items-center gap-3.5">
                <a href="/" class="flex items-center gap-3 group">
                    <div class="p-1 bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-white/20 dark:border-slate-700/60 logo-glow flex items-center justify-center">
                        <img src="/logo.png" alt="MAG Healthcare Solutions" class="h-10 w-10 sm:h-11 sm:w-11 object-contain rounded-xl">
                    </div>
                    <div>
                        <span id="i18n-appTitle" class="text-2xl font-black tracking-tight font-sans text-white group-hover:text-emerald-100 transition">MediDemand</span>
                        <span class="text-[10px] font-semibold text-emerald-200/90 tracking-wide block">MAG Healthcare Solutions</span>
                    </div>
                </a>
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

                <!-- User Session / Login Button -->
                <div id="userProfileArea" class="flex items-center gap-2">
                    <button type="button" id="loginHeaderBtn" onclick="toggleAuthModal()" class="text-xs bg-white dark:bg-emerald-100 text-emerald-800 hover:bg-emerald-50 dark:hover:bg-white px-3.5 py-1.5 rounded-xl font-bold shadow-sm transition cursor-pointer flex items-center gap-1.5">
                        <i class="fa-solid fa-user"></i>
                        <span id="i18n-loginBtn">تسجيل الدخول</span>
                    </button>

                    <div id="userProfileBadge" class="hidden flex items-center gap-2">
                        <div class="flex items-center gap-1.5 bg-emerald-800/90 dark:bg-emerald-950/90 text-emerald-100 px-3 py-1.5 rounded-xl border border-emerald-600/70 shadow-sm text-xs font-bold">
                            <span id="userAvatarIcon" class="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center text-[10px] text-white uppercase font-bold">U</span>
                            <span id="currentUserName" class="max-w-[120px] truncate">المستخدم</span>
                        </div>
                        <button type="button" onclick="handleLogout()" title="تسجيل الخروج / Sign Out" class="p-1.5 bg-white/15 hover:bg-rose-500/80 border border-white/20 text-white rounded-xl text-xs transition cursor-pointer">
                            <i class="fa-solid fa-right-from-bracket"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <!-- Auth Warning Banner -->
        <div id="authBanner" class="mb-6 p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-2xl flex items-center justify-between shadow-sm transition-colors">
            <div class="flex items-center gap-3">
                <i class="fa-solid fa-shield-halved text-amber-600 dark:text-amber-400 text-xl"></i>
                <div>
                    <h3 id="i18n-authBannerTitle" class="font-bold text-amber-900 dark:text-amber-200 text-sm">تسجيل الدخول متاح</h3>
                    <p id="i18n-authBannerDesc" class="text-xs text-amber-700 dark:text-amber-300/80">يمكنك تسجيل الدخول عبر حساب Google أو بريدك الإلكتروني لتوثيق السجلات باسمك.</p>
                </div>
            </div>
            <button type="button" onclick="toggleAuthModal()" id="i18n-authBannerBtn" class="bg-amber-600 hover:bg-amber-700 text-white text-xs px-4 py-2 rounded-xl font-bold shadow-sm transition cursor-pointer">
                تسجيل الدخول
            </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Forecast Input Form (Exact match to medical requirements) -->
            <div class="lg:col-span-6">
                <div class="bg-white dark:bg-darkcard rounded-3xl p-6 shadow-sm dark:shadow-2xl border border-slate-200/80 dark:border-slate-700/80 transition-colors">
                    <div class="flex items-center gap-2 mb-5 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                        <i class="fa-solid fa-calculator text-emerald-600 dark:text-emerald-400 text-lg"></i>
                        <h2 id="i18n-formTitle" class="font-bold text-slate-800 dark:text-white text-lg">بيانات واحتساب طلبية الصنف</h2>
                    </div>

                        <!-- Row 1: Facility Name (Right) & User Name (Left) -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label id="i18n-labelFacility" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم المنشأة</label>
                                <input type="text" id="facilityName" placeholder="مثال: مستشفى الكرنك الدولي"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                            </div>
                            <div>
                                <label id="i18n-labelUser" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم المستخدم</label>
                                <input type="text" id="userName" placeholder="مثال: د. ماجد عاطف"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none">
                            </div>
                        </div>

                        <!-- Row 2: Drug Name (Right) & Month 1 Consumption (Left) -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label id="i18n-labelDrug" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">اسم الصنف</label>
                                <input type="text" id="drugName" required placeholder="e.g. Paracetamol 500mg" dir="ltr"
                                    oninput="onDrugNameInput(this)"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-sans">
                                <p id="drugNameError" class="hidden text-[11px] text-rose-500 dark:text-rose-400 font-bold mt-1 flex items-center gap-1 animate-pulse">
                                    <i class="fa-solid fa-triangle-exclamation"></i>
                                    <span id="i18n-drugNameError">يجب كتابة اسم الصنف بالحروف الإنجليزية فقط</span>
                                </p>
                            </div>

                            <div>
                                <label id="i18n-labelM1" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">استهلاك الشهر الأول</label>
                                <input type="number" step="any" min="0" id="m1Consumption" required placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                        </div>

                        <!-- Row 3: Month 2 Consumption (Right) & Month 3 Consumption (Left) -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label id="i18n-labelM2" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">استهلاك الشهر الثاني</label>
                                <input type="number" step="any" min="0" id="m2Consumption" required placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>

                            <div>
                                <label id="i18n-labelM3" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">استهلاك الشهر الثالث</label>
                                <input type="number" step="any" min="0" id="m3Consumption" required placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                        </div>

                        <!-- Row 4: Lead Days (Right) & Safety Days (Left) -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label id="i18n-labelLead" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">فترة التوريد (بالأيام)</label>
                                <input type="number" step="1" min="0" value="30" id="leadDays" oninput="onLeadDaysChange()" placeholder="30"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>

                            <div>
                                <label id="i18n-labelSafety" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">كفاية رصيد الأمان (بالأيام)</label>
                                <input type="number" step="1" min="0" value="15" id="safetyDays" oninput="liveUpdateCalculation()" placeholder="15"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                        </div>

                        <!-- Row 5: Current Stock (Right) -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label id="i18n-labelStock" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">المخزون الحالي</label>
                                <input type="number" step="any" min="0" id="currentStock" placeholder="0" oninput="liveUpdateCalculation()"
                                    class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900 text-slate-900 dark:text-white transition outline-none font-semibold">
                            </div>
                            <div class="hidden sm:block"></div>
                        </div>

                        <!-- Result Card with Live Breakdown -->
                        <div class="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/50 dark:to-teal-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-2xl mt-4 transition-colors">
                            <div class="text-xs text-emerald-800 dark:text-emerald-300 font-bold mb-1 flex items-center justify-between">
                                <span id="i18n-resultTitle">الكمية المقترح طلبها (Recommended Order):</span>
                                <span id="liveTotalDaysBadge" class="text-[10px] bg-emerald-200/60 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded-full font-bold">تغطية 45 يوم</span>
                            </div>
                            <div class="flex items-baseline justify-between my-1">
                                <span id="liveResult" class="text-4xl font-black text-emerald-700 dark:text-emerald-400 font-mono">0</span>
                                <span id="i18n-resultUnit" class="text-xs text-emerald-600 dark:text-emerald-300 font-bold">عبوة / وحدة</span>
                            </div>
                            
                            <!-- Calculation summary breakdown -->
                            <div class="mt-2.5 pt-2 border-t border-emerald-200/70 dark:border-emerald-800/50 grid grid-cols-2 gap-2 text-[11px] text-emerald-800 dark:text-emerald-300">
                                <div><span id="i18n-lblAvgMonthly" class="text-emerald-600 dark:text-emerald-400">متوسط الاستهلاك:</span> <span id="calcAvg" class="font-mono font-bold">0</span> <span id="i18n-unitMonth">/ شهر</span></div>
                                <div><span id="i18n-lblDailyDemand" class="text-emerald-600 dark:text-emerald-400">الاستهلاك اليومي:</span> <span id="calcDaily" class="font-mono font-bold">0</span> <span id="i18n-unitDay">/ يوم</span></div>
                            </div>
                        </div>

                        <button type="submit" id="submitBtn"
                            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white font-bold rounded-xl shadow-md hover:shadow-lg transition flex items-center justify-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-check-double"></i>
                            <span id="i18n-submitBtn">حفظ وتأكيد الطلبية</span>
                        </button>
                    </form>
                </div>
            </div>

            <!-- Stats & Historical Submissions -->
            <div class="lg:col-span-6 space-y-6">
                <!-- KPI Mini Cards -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-white dark:bg-darkcard p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm stat-card">
                        <div id="i18n-kpiTotalItems" class="text-slate-400 dark:text-slate-400 text-xs font-bold mb-1">إجمالي الأصناف المسجلة</div>
                        <div id="totalItemsCount" class="text-2xl font-black text-slate-800 dark:text-white font-mono">0</div>
                    </div>
                    <div class="bg-white dark:bg-darkcard p-4 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm stat-card">
                        <div id="i18n-kpiTotalQty" class="text-slate-400 dark:text-slate-400 text-xs font-bold mb-1">إجمالي الكميات المطلوبة</div>
                        <div id="totalQtySum" class="text-2xl font-black text-emerald-600 dark:text-emerald-400 font-mono">0</div>
                    </div>
                </div>

                <!-- History Table -->
                <div class="bg-white dark:bg-darkcard rounded-3xl p-6 shadow-sm dark:shadow-2xl border border-slate-200/80 dark:border-slate-700/80 transition-colors">
                    <div class="flex flex-wrap justify-between items-center gap-3 mb-4 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-clock-rotate-left text-slate-500 dark:text-slate-400"></i>
                            <h3 id="i18n-historyTitle" class="font-bold text-slate-800 dark:text-white text-base">سجل الطلبيات المحفوظة</h3>
                        </div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <input type="text" id="tableSearch" oninput="filterTable()" placeholder="بحث عن صنف..."
                                class="px-3 py-1.5 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-lg text-xs outline-none focus:ring-1 focus:ring-emerald-500 text-slate-900 dark:text-white">
                            
                            <button type="button" onclick="exportToCSV()" class="text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1 cursor-pointer">
                                <i class="fa-solid fa-file-csv text-emerald-600 dark:text-emerald-400"></i> <span id="i18n-exportBtn">تصدير CSV</span>
                            </button>

                            <button type="button" onclick="clearAllData()" title="مسح كافة البيانات / Clear All Records" class="text-xs bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/50 dark:hover:bg-rose-900/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800/60 px-2.5 py-1.5 rounded-lg font-bold transition flex items-center gap-1 cursor-pointer">
                                <i class="fa-solid fa-trash-can text-rose-600 dark:text-rose-400"></i> <span id="i18n-clearBtn">مسح</span>
                            </button>
                        </div>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-xs">
                            <thead class="bg-slate-50 dark:bg-slate-900/60 text-slate-600 dark:text-slate-300 font-bold border-b border-slate-200 dark:border-slate-700">
                                <tr>
                                    <th id="i18n-thTime" class="py-3 px-3">Date & Time</th>
                                    <th id="i18n-thDrug" class="py-3 px-3">الصنف</th>
                                    <th id="i18n-thAvg" class="py-3 px-3">م. 3 أشهر</th>
                                    <th id="i18n-thStock" class="py-3 px-3">المخزون</th>
                                    <th id="i18n-thDays" class="py-3 px-3">الأيام</th>
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

    <!-- Footer -->
    <footer class="mt-auto border-t border-slate-200/80 dark:border-slate-800 py-4 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
            <div class="flex items-center gap-2">
                <img src="/logo.png" alt="MAG" class="h-5 w-5 object-contain">
                <span class="font-bold text-slate-700 dark:text-slate-300">MAG Healthcare Solutions</span>
                <span>• MediDemand v5.1</span>
            </div>
            <div>
                <span>جميع الحقوق محفوظة © 2026</span>
            </div>
        </div>
    </footer>

    <!-- Modern Google / Email Authentication Modal -->
    <div id="authModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center hidden">
        <div class="bg-white dark:bg-darkcard rounded-3xl p-6 max-w-md w-full mx-4 shadow-2xl border border-slate-100 dark:border-slate-700 relative">
            <button type="button" onclick="toggleAuthModal()" class="absolute top-4 end-4 text-slate-400 hover:text-slate-600 dark:hover:text-white p-2 rounded-full cursor-pointer">
                <i class="fa-solid fa-xmark text-lg"></i>
            </button>

            <!-- Header -->
            <div class="text-center mb-5">
                <div class="w-14 h-14 bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-md border border-slate-100 dark:border-slate-700 mx-auto mb-2.5 flex items-center justify-center logo-glow">
                    <img src="/logo.png" alt="MAG Logo" class="h-full w-full object-contain rounded-xl">
                </div>
                <h3 id="i18n-authModalTitle" class="font-black text-slate-800 dark:text-white text-lg">تسجيل الدخول لمنظومة MediDemand</h3>
                <p id="i18n-authModalDesc" class="text-xs text-slate-500 dark:text-slate-400 mt-1">اختر طريقة تسجيل الدخول المناسبة لك للمتابعة</p>
            </div>

            <!-- 1. Google One-Click Sign In -->
            <div class="mb-5">
                <button type="button" onclick="handleGoogleSignIn()" class="w-full py-2.5 px-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm text-xs font-bold text-slate-700 dark:text-slate-100 flex items-center justify-center gap-3 transition cursor-pointer group">
                    <svg class="w-4 h-4" viewBox="0 0 24 24">
                        <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.3 8.9 5 12 5z"/>
                        <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/>
                        <path fill="#FBBC05" d="M5.3 14.7c-.2-.7-.4-1.5-.4-2.7s.1-2 .4-2.7L1.6 6.4C.6 8.4 0 10.6 0 13s.6 4.6 1.6 6.6l3.7-4.9z"/>
                        <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.3-6.7-5.3L1.6 16c1.9 3.8 5.8 7 10.4 7z"/>
                    </svg>
                    <span id="i18n-btnGoogleLogin">المتابعة باستخدام حساب Google</span>
                </button>
            </div>

            <!-- Divider -->
            <div class="relative flex py-2 items-center mb-4">
                <div class="flex-grow border-t border-slate-200 dark:border-slate-700"></div>
                <span id="i18n-authOr" class="flex-shrink mx-3 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">أو عبر البريد الإلكتروني</span>
                <div class="flex-grow border-t border-slate-200 dark:border-slate-700"></div>
            </div>

            <!-- Tabs: Sign In / Register -->
            <div class="flex border-b border-slate-200 dark:border-slate-700 mb-4 text-xs font-semibold">
                <button type="button" onclick="switchAuthTab('login')" id="tabLogin" class="flex-1 py-2 text-center auth-tab-active transition cursor-pointer">
                    <span id="i18n-tabLoginText">تسجيل الدخول</span>
                </button>
                <button type="button" onclick="switchAuthTab('register')" id="tabRegister" class="flex-1 py-2 text-center text-slate-500 dark:text-slate-400 hover:text-emerald-600 transition cursor-pointer">
                    <span id="i18n-tabRegisterText">حساب جديد</span>
                </button>
            </div>

            <!-- Form -->
            <form id="authEmailForm" onsubmit="handleEmailAuth(event)" class="space-y-3.5">
                <div id="authNameField" class="hidden">
                    <label id="i18n-authLabelName" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">الاسم الكامل / الصفة</label>
                    <input type="text" id="authNameInput" placeholder="مثال: د. ماجد عاطف"
                        class="w-full px-3.5 py-2 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-xs outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-white">
                </div>

                <div>
                    <label id="i18n-authLabelEmail" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">البريد الإلكتروني</label>
                    <input type="email" id="authEmailInput" required placeholder="doctor@hospital.gov.eg"
                        class="w-full px-3.5 py-2 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-xs outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-white font-mono">
                </div>

                <div>
                    <label id="i18n-authLabelPass" class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">كلمة المرور</label>
                    <input type="password" id="authPassInput" required placeholder="••••••••"
                        class="w-full px-3.5 py-2 bg-slate-50 dark:bg-darkinput border border-slate-200 dark:border-slate-700 rounded-xl text-xs outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-white font-mono">
                </div>

                <button type="submit" id="authSubmitBtn" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white font-bold rounded-xl text-xs shadow-md transition cursor-pointer flex items-center justify-center gap-2">
                    <i class="fa-solid fa-arrow-right-to-bracket"></i>
                    <span id="i18n-authSubmitText">دخول</span>
                </button>
            </form>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="toast" class="fixed bottom-6 start-6 bg-slate-900 dark:bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-2xl shadow-2xl text-xs flex items-center gap-2 transform translate-y-20 opacity-0 transition-all duration-300 z-50">
        <i id="toastIcon" class="fa-solid fa-circle-check text-emerald-400"></i>
        <span id="toastMsg">تم بنجاح</span>
    </div>

    <script>
        let currentLang = localStorage.getItem('drug_forecast_lang') || 'ar';
        let currentUser = JSON.parse(localStorage.getItem('medi_demand_user') || 'null');
        let currentAuthTab = 'login';
        let records = JSON.parse(localStorage.getItem('forecast_records') || '[]');

        const translations = {
            ar: {
                appTitle: "MediDemand",
                langToggle: "English",
                themeDark: "الوضع الليلي",
                themeLight: "الوضع النهاري",
                loginBtn: "تسجيل الدخول",
                logoutBtn: "تسجيل الخروج",
                authBannerTitle: "تسجيل الدخول متاح",
                authBannerDesc: "يمكنك تسجيل الدخول عبر حساب Google أو بريدك الإلكتروني لتوثيق السجلات باسمك.",
                authBannerBtn: "تسجيل الدخول",
                formTitle: "بيانات واحتساب طلبية الصنف",
                labelDrug: "اسم الصنف (English Only)",
                placeholderDrug: "e.g. Paracetamol 500mg / Ceftriaxone 1g",
                drugNameError: "يجب كتابة اسم الصنف بالحروف الإنجليزية فقط",
                labelM1: "استهلاك الشهر الأول",
                labelM2: "استهلاك الشهر الثاني",
                labelM3: "استهلاك الشهر الثالث",
                labelLead: "فترة التوريد (بالأيام)",
                leadHint: "مدة وصول الشحنة من المورد للمخزن",
                labelSafety: "كفاية رصيد الأمان (بالأيام)",
                safetyHint: "عدد أيام المخزون الاحتياطي للطوارئ",
                labelStock: "المخزون الحالي بالمستودع",
                labelFacility: "اسم المنشأة / المستشفى",
                placeholderFacility: "مستشفى الكرنك الدولي",
                labelUser: "الصيدلي المسؤول",
                placeholderUser: "د. الصيدلي",
                resultTitle: "الكمية المقترح طلبها (Recommended Order):",
                resultUnit: "عبوة / وحدة",
                lblAvgMonthly: "متوسط الاستهلاك:",
                unitMonth: "/ شهر",
                lblDailyDemand: "الاستهلاك اليومي:",
                unitDay: "/ يوم",
                badgeDaysCoverage: "تغطية {days} يوم ({lead} توريد + {safety} أمان)",
                autoSafetyBadge: "تلقائي (50% توريد)",
                daysUnit: "يوم",
                submitBtn: "حفظ وتأكيد الطلبية",
                kpiTotalItems: "إجمالي الأصناف المسجلة",
                kpiTotalQty: "إجمالي الكميات المطلوبة",
                historyTitle: "سجل الطلبيات المحفوظة",
                searchPlaceholder: "بحث عن صنف...",
                exportBtn: "تصدير CSV",
                clearBtn: "مسح",
                confirmClear: "هل أنت متأكد من رغبتك في مسح كافة السجلات المحفوظة؟",
                clearOkToast: "تم مسح كافة البيانات بنجاح",
                thTime: "Date & Time",
                thDrug: "الصنف",
                thAvg: "م. 3 أشهر",
                thStock: "المخزون",
                thDays: "الأيام",
                thRec: "الكمية المقترحة",
                loadingRows: "لا توجد طلبات مسجلة حتى الآن",
                emptyRows: "لا توجد طلبات مسجلة حتى الآن",
                noMatchRows: "لا توجد نتائج مطابقة للبحث",
                
                authModalTitle: "تسجيل الدخول لمنظومة MediDemand",
                authModalDesc: "اختر طريقة تسجيل الدخول المناسبة لك للمتابعة",
                btnGoogleLogin: "المتابعة باستخدام حساب Google",
                authOr: "أو عبر البريد الإلكتروني",
                tabLoginText: "تسجيل الدخول",
                tabRegisterText: "حساب جديد",
                authLabelName: "الاسم الكامل / الصفة",
                placeholderName: "مثال: د. ماجد عاطف",
                authLabelEmail: "البريد الإلكتروني",
                authLabelPass: "كلمة المرور",
                authSubmitLogin: "دخول",
                authSubmitRegister: "إنشاء حساب ومتابعة",
                toastLoginOk: "تم تسجيل الدخول بنجاح. مرحباً بك د. {name}",
                toastRegisterOk: "تم إنشاء الحساب بنجاح وتسجيل الدخول",
                toastLogoutOk: "تم تسجيل الخروج",
                toastDrugMustBeEnglish: "يرجى كتابة اسم الصنف باللغة الإنجليزية فقط (English Letters Only)",
                toastSavedOk: "تم حفظ طلبية الصنف ({drug}) بكمية: {qty}",
                exportNoData: "لا توجد بيانات لتصديرها",
                csvHeader: "\uFEFFDate & Time,Drug Name,Month 1,Month 2,Month 3,Avg Monthly,Lead Days,Safety Days,Current Stock,Recommended Order\n"
            },
            en: {
                appTitle: "MediDemand",
                langToggle: "العربية",
                themeDark: "Dark Mode",
                themeLight: "Light Mode",
                loginBtn: "Sign In",
                logoutBtn: "Sign Out",
                authBannerTitle: "Sign In Available",
                authBannerDesc: "Sign in with Google or your work email to authenticate orders under your name.",
                authBannerBtn: "Sign In",
                formTitle: "Drug Item Forecast & Order Calculator",
                labelDrug: "Drug Name (English Only)",
                placeholderDrug: "e.g. Paracetamol 500mg / Ceftriaxone 1g",
                drugNameError: "Drug name must be entered in English letters only",
                labelM1: "Month 1 Consumption",
                labelM2: "Month 2 Consumption",
                labelM3: "Month 3 Consumption",
                labelLead: "Lead Time (Days)",
                leadHint: "Delivery duration from supplier to warehouse",
                labelSafety: "Safety Stock Coverage (Days)",
                safetyHint: "Buffer stock coverage days for emergencies",
                labelStock: "Current Stock on Hand",
                labelFacility: "Facility / Hospital",
                placeholderFacility: "Karnak International Hospital",
                labelUser: "Pharmacist in Charge",
                placeholderUser: "Dr. Pharmacist",
                resultTitle: "Recommended Order Quantity:",
                resultUnit: "Packs / Units",
                lblAvgMonthly: "Avg Consumption:",
                unitMonth: "/ mo",
                lblDailyDemand: "Daily Demand:",
                unitDay: "/ day",
                badgeDaysCoverage: "{days} Days Coverage ({lead} Lead + {safety} Safety)",
                autoSafetyBadge: "Auto (50% Lead)",
                daysUnit: "Days",
                submitBtn: "Save & Confirm Order",
                kpiTotalItems: "Total Recorded Drugs",
                kpiTotalQty: "Total Ordered Quantity",
                historyTitle: "Saved Drug Orders History",
                searchPlaceholder: "Search drug...",
                exportBtn: "Export CSV",
                clearBtn: "Clear",
                confirmClear: "Are you sure you want to clear all recorded orders?",
                clearOkToast: "All records cleared successfully",
                thTime: "Date & Time",
                thDrug: "Drug Item",
                thAvg: "3-Mo Avg",
                thStock: "Stock",
                thDays: "Days",
                thRec: "Recommended Qty",
                loadingRows: "No orders recorded yet",
                emptyRows: "No orders recorded yet",
                noMatchRows: "No matching records found",
                
                authModalTitle: "Sign in to MediDemand",
                authModalDesc: "Choose your preferred sign-in method to continue",
                btnGoogleLogin: "Continue with Google",
                authOr: "Or with email",
                tabLoginText: "Sign In",
                tabRegisterText: "Create Account",
                authLabelName: "Full Name / Title",
                placeholderName: "e.g. Dr. Magid Atif",
                authLabelEmail: "Email Address",
                authLabelPass: "Password",
                authSubmitLogin: "Sign In",
                authSubmitRegister: "Register & Continue",
                toastLoginOk: "Signed in successfully. Welcome Dr. {name}",
                toastRegisterOk: "Account created and signed in successfully",
                toastLogoutOk: "Signed out successfully",
                toastDrugMustBeEnglish: "Drug name must be in English letters only",
                toastSavedOk: "Order saved for ({drug}) with qty: {qty}",
                exportNoData: "No data available to export",
                csvHeader: "\uFEFFDate & Time,Drug Name,Month 1,Month 2,Month 3,Avg Monthly,Lead Days,Safety Days,Current Stock,Recommended Order\n"
            }
        };

        function onDrugNameInput(input) {
            const hasArabic = /[\u0600-\u06FF]/.test(input.value);
            const err = document.getElementById('drugNameError');
            if (hasArabic) {
                if (err) err.classList.remove('hidden');
                input.classList.add('border-rose-500', 'focus:ring-rose-500', 'bg-rose-50/20');
            } else {
                if (err) err.classList.add('hidden');
                input.classList.remove('border-rose-500', 'focus:ring-rose-500', 'bg-rose-50/20');
            }
        }

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
            document.getElementById('i18n-loginBtn').textContent = t.loginBtn;

            document.getElementById('i18n-authBannerTitle').textContent = t.authBannerTitle;
            document.getElementById('i18n-authBannerDesc').textContent = t.authBannerDesc;
            document.getElementById('i18n-authBannerBtn').textContent = t.authBannerBtn;

            document.getElementById('i18n-formTitle').textContent = t.formTitle;
            document.getElementById('i18n-labelDrug').textContent = t.labelDrug;
            document.getElementById('drugName').placeholder = t.placeholderDrug;
            document.getElementById('i18n-drugNameError').textContent = t.drugNameError;

            document.getElementById('i18n-labelM1').textContent = t.labelM1;
            document.getElementById('i18n-labelM2').textContent = t.labelM2;
            document.getElementById('i18n-labelM3').textContent = t.labelM3;

            document.getElementById('i18n-labelLead').textContent = t.labelLead;
            const leadHintEl = document.getElementById('i18n-leadHint');
            if (leadHintEl) leadHintEl.textContent = t.leadHint;
            document.getElementById('i18n-labelSafety').textContent = t.labelSafety;
            const autoSafetyEl = document.getElementById('i18n-autoSafetyBadge');
            if (autoSafetyEl) autoSafetyEl.textContent = t.autoSafetyBadge;
            const safetyHintEl = document.getElementById('i18n-safetyHint');
            if (safetyHintEl) safetyHintEl.textContent = t.safetyHint;

            document.getElementById('i18n-labelStock').textContent = t.labelStock;
            document.getElementById('i18n-labelFacility').textContent = t.labelFacility;
            document.getElementById('facilityName').placeholder = t.placeholderFacility;
            document.getElementById('i18n-labelUser').textContent = t.labelUser;
            document.getElementById('userName').placeholder = t.placeholderUser;

            document.getElementById('i18n-resultTitle').textContent = t.resultTitle;
            document.getElementById('i18n-resultUnit').textContent = t.resultUnit;
            const lblAvgEl = document.getElementById('i18n-lblAvgMonthly');
            if (lblAvgEl) lblAvgEl.textContent = t.lblAvgMonthly;
            const unitMoEl = document.getElementById('i18n-unitMonth');
            if (unitMoEl) unitMoEl.textContent = t.unitMonth;
            const lblDailyEl = document.getElementById('i18n-lblDailyDemand');
            if (lblDailyEl) lblDailyEl.textContent = t.lblDailyDemand;
            const unitDayEl = document.getElementById('i18n-unitDay');
            if (unitDayEl) unitDayEl.textContent = t.unitDay;
            document.getElementById('i18n-submitBtn').textContent = t.submitBtn;

            document.getElementById('i18n-kpiTotalItems').textContent = t.kpiTotalItems;
            document.getElementById('i18n-kpiTotalQty').textContent = t.kpiTotalQty;

            document.getElementById('i18n-historyTitle').textContent = t.historyTitle;
            document.getElementById('tableSearch').placeholder = t.searchPlaceholder;
            document.getElementById('i18n-exportBtn').textContent = t.exportBtn;
            const clearBtn = document.getElementById('i18n-clearBtn');
            if (clearBtn) clearBtn.textContent = t.clearBtn;

            document.getElementById('i18n-thTime').textContent = t.thTime;
            document.getElementById('i18n-thDrug').textContent = t.thDrug;
            document.getElementById('i18n-thAvg').textContent = t.thAvg;
            document.getElementById('i18n-thStock').textContent = t.thStock;
            document.getElementById('i18n-thDays').textContent = t.thDays;
            document.getElementById('i18n-thRec').textContent = t.thRec;
            liveUpdateCalculation();

            // Auth Modal translations
            document.getElementById('i18n-authModalTitle').textContent = t.authModalTitle;
            document.getElementById('i18n-authModalDesc').textContent = t.authModalDesc;
            document.getElementById('i18n-btnGoogleLogin').textContent = t.btnGoogleLogin;
            document.getElementById('i18n-authOr').textContent = t.authOr;
            document.getElementById('i18n-tabLoginText').textContent = t.tabLoginText;
            document.getElementById('i18n-tabRegisterText').textContent = t.tabRegisterText;
            document.getElementById('i18n-authLabelName').textContent = t.authLabelName;
            document.getElementById('authNameInput').placeholder = t.placeholderName;
            document.getElementById('i18n-authLabelEmail').textContent = t.authLabelEmail;
            document.getElementById('i18n-authLabelPass').textContent = t.authLabelPass;
            document.getElementById('i18n-authSubmitText').textContent = currentAuthTab === 'login' ? t.authSubmitLogin : t.authSubmitRegister;

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

        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            const icon = document.getElementById('toastIcon');
            const msgEl = document.getElementById('toastMsg');
            if (!toast) return;
            msgEl.textContent = msg;
            icon.className = isError ? "fa-solid fa-circle-exclamation text-rose-400" : "fa-solid fa-circle-check text-emerald-400";
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 3500);
        }

        function updateAuthStateUI() {
            const banner = document.getElementById('authBanner');
            const loginBtn = document.getElementById('loginHeaderBtn');
            const profileBadge = document.getElementById('userProfileBadge');
            const userNameEl = document.getElementById('currentUserName');
            const avatarEl = document.getElementById('userAvatarIcon');
            const userField = document.getElementById('userName');

            if (currentUser && currentUser.email) {
                if (banner) banner.classList.add('hidden');
                if (loginBtn) loginBtn.classList.add('hidden');
                if (profileBadge) profileBadge.classList.remove('hidden');
                
                const displayName = currentUser.name || currentUser.email.split('@')[0];
                if (userNameEl) userNameEl.textContent = displayName;
                if (avatarEl) avatarEl.textContent = displayName.charAt(0).toUpperCase();
                
                if (userField && !userField.value) {
                    userField.value = displayName;
                }
            } else {
                if (banner) banner.classList.remove('hidden');
                if (loginBtn) loginBtn.classList.remove('hidden');
                if (profileBadge) profileBadge.classList.add('hidden');
            }
        }

        function initApp() {
            setLanguage(currentLang);
            initTheme();
            updateAuthStateUI();
            renderTable();
            updateKPIs();
            liveUpdateCalculation();
        }

        function clearAllData() {
            const t = translations[currentLang];
            if (!confirm(t.confirmClear)) return;

            records = [];
            localStorage.removeItem('forecast_records');
            renderTable();
            updateKPIs();
            showToast(t.clearOkToast);
        }

        function toggleAuthModal() {
            const modal = document.getElementById('authModal');
            if (modal) modal.classList.toggle('hidden');
        }

        function switchAuthTab(tab) {
            currentAuthTab = tab;
            const t = translations[currentLang];
            const tabLogin = document.getElementById('tabLogin');
            const tabRegister = document.getElementById('tabRegister');
            const nameField = document.getElementById('authNameField');
            const submitText = document.getElementById('i18n-authSubmitText');

            if (tab === 'register') {
                tabRegister.className = "flex-1 py-2 text-center auth-tab-active transition cursor-pointer";
                tabLogin.className = "flex-1 py-2 text-center text-slate-500 dark:text-slate-400 hover:text-emerald-600 transition cursor-pointer";
                nameField.classList.remove('hidden');
                submitText.textContent = t.authSubmitRegister;
            } else {
                tabLogin.className = "flex-1 py-2 text-center auth-tab-active transition cursor-pointer";
                tabRegister.className = "flex-1 py-2 text-center text-slate-500 dark:text-slate-400 hover:text-emerald-600 transition cursor-pointer";
                nameField.classList.add('hidden');
                submitText.textContent = t.authSubmitLogin;
            }
        }

        function handleGoogleSignIn() {
            const t = translations[currentLang];
            const promptEmail = prompt(currentLang === 'ar' ? 'أدخل بريدك الإلكتروني لحساب Google للمتابعة:' : 'Enter your Google Account email to continue:', 'dr.magid.atif@gmail.com');
            if (!promptEmail) return;

            const nameParts = promptEmail.split('@')[0].replace('.', ' ');
            const formattedName = nameParts.charAt(0).toUpperCase() + nameParts.slice(1);

            currentUser = {
                email: promptEmail,
                name: formattedName,
                provider: 'google'
            };

            localStorage.setItem('medi_demand_user', JSON.stringify(currentUser));
            updateAuthStateUI();
            toggleAuthModal();
            showToast(t.toastLoginOk.replace('{name}', currentUser.name));
        }

        function handleEmailAuth(e) {
            e.preventDefault();
            const t = translations[currentLang];
            const email = document.getElementById('authEmailInput').value.trim();
            const name = document.getElementById('authNameInput').value.trim() || email.split('@')[0];

            currentUser = {
                name: name,
                email: email,
                provider: 'email'
            };

            localStorage.setItem('medi_demand_user', JSON.stringify(currentUser));
            updateAuthStateUI();
            toggleAuthModal();
            showToast(currentAuthTab === 'register' ? t.toastRegisterOk : t.toastLoginOk.replace('{name}', currentUser.name));
        }

        function handleLogout() {
            const t = translations[currentLang];
            currentUser = null;
            localStorage.removeItem('medi_demand_user');
            updateAuthStateUI();
            showToast(t.toastLogoutOk);
        }

        // Exact Formula based on 3 Months Consumption + Lead Days + Safety Days - Current Stock
        function computeForecast(m1, m2, m3, leadDays, safetyDays, currentStock) {
            const avgMonthly = (m1 + m2 + m3) / 3.0;
            const dailyDemand = avgMonthly / 30.0;
            const totalDays = leadDays + safetyDays;
            const totalRequired = dailyDemand * totalDays;
            const netOrder = totalRequired - currentStock;
            return {
                recommendedQty: Math.max(0, Math.round(netOrder)),
                avgMonthly: Math.round(avgMonthly * 10) / 10,
                dailyDemand: Math.round(dailyDemand * 100) / 100,
                totalDays: totalDays
            };
        }

        function onLeadDaysChange() {
            const lead = parseFloat(document.getElementById('leadDays').value) || 0;
            // Standard Healthcare/Pharma Formula: Safety stock covers 50% of lead time
            const autoSafety = Math.max(0, Math.round(lead / 2));
            document.getElementById('safetyDays').value = autoSafety;
            liveUpdateCalculation();
        }

        function liveUpdateCalculation() {
            const m1 = parseFloat(document.getElementById('m1Consumption').value) || 0;
            const m2 = parseFloat(document.getElementById('m2Consumption').value) || 0;
            const m3 = parseFloat(document.getElementById('m3Consumption').value) || 0;
            const leadDays = parseFloat(document.getElementById('leadDays').value) || 0;
            const safetyDays = parseFloat(document.getElementById('safetyDays').value) || 0;
            const stock = parseFloat(document.getElementById('currentStock').value) || 0;

            const res = computeForecast(m1, m2, m3, leadDays, safetyDays, stock);

            const t = translations[currentLang];
            document.getElementById('liveResult').textContent = res.recommendedQty.toLocaleString('en-US');
            document.getElementById('calcAvg').textContent = res.avgMonthly.toLocaleString('en-US');
            document.getElementById('calcDaily').textContent = res.dailyDemand.toLocaleString('en-US');
            
            const badgeText = t.badgeDaysCoverage
                .replace('{days}', res.totalDays)
                .replace('{lead}', leadDays)
                .replace('{safety}', safetyDays);
            document.getElementById('liveTotalDaysBadge').textContent = badgeText;
        }

        function handleCalculate(e) {
            e.preventDefault();
            const drug = document.getElementById('drugName').value.trim();
            const m1 = parseFloat(document.getElementById('m1Consumption').value) || 0;
            const m2 = parseFloat(document.getElementById('m2Consumption').value) || 0;
            const m3 = parseFloat(document.getElementById('m3Consumption').value) || 0;
            const leadDays = parseFloat(document.getElementById('leadDays').value) || 0;
            const safetyDays = parseFloat(document.getElementById('safetyDays').value) || 0;
            const stock = parseFloat(document.getElementById('currentStock').value) || 0;
            const facility = document.getElementById('facilityName').value.trim() || 'العام';
            const user = document.getElementById('userName').value.trim() || 'المسؤول';
            const t = translations[currentLang];

            // Validation: Drug name MUST be in English only
            if (/[\u0600-\u06FF]/.test(drug)) {
                showToast(t.toastDrugMustBeEnglish, true);
                const drugInput = document.getElementById('drugName');
                if (drugInput) {
                    drugInput.focus();
                    onDrugNameInput(drugInput);
                }
                return;
            }

            const calc = computeForecast(m1, m2, m3, leadDays, safetyDays, stock);
            const now = new Date();
            const pad = n => (n < 10 ? '0' + n : n);
            const timestampStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

            const record = {
                timestamp: timestampStr,
                facilityName: facility,
                userName: user,
                drugName: drug,
                m1: m1,
                m2: m2,
                m3: m3,
                avgMonthly: calc.avgMonthly,
                leadDays: leadDays,
                safetyDays: safetyDays,
                totalDays: calc.totalDays,
                currentStock: stock,
                recommendedQty: calc.recommendedQty
            };

            records.unshift(record);
            localStorage.setItem('forecast_records', JSON.stringify(records));
            renderTable();
            updateKPIs();

            const msg = t.toastSavedOk.replace('{drug}', drug).replace('{qty}', calc.recommendedQty);
            showToast(msg);

            document.getElementById('drugName').value = '';
            const errEl = document.getElementById('drugNameError');
            if (errEl) errEl.classList.add('hidden');
            document.getElementById('m1Consumption').value = '';
            document.getElementById('m2Consumption').value = '';
            document.getElementById('m3Consumption').value = '';
            document.getElementById('currentStock').value = '';
            liveUpdateCalculation();
        }

        function renderTable(filterText = '') {
            const tbody = document.getElementById('historyTableBody');
            if (!tbody) return;
            const t = translations[currentLang];
            const filtered = records.filter(r => 
                !filterText || 
                (r.drugName && r.drugName.toLowerCase().includes(filterText.toLowerCase())) || 
                (r.facilityName && r.facilityName.toLowerCase().includes(filterText.toLowerCase()))
            );

            if (filtered.length === 0) {
                const emptyMsg = records.length === 0 ? t.emptyRows : t.noMatchRows;
                tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-400 dark:text-slate-500">${emptyMsg}</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(r => `
                <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/50 transition">
                    <td class="py-3 px-3 text-slate-500 dark:text-slate-400 font-mono text-[11px]" dir="ltr">${r.timestamp || '-'}</td>
                    <td class="py-3 px-3 font-bold text-slate-900 dark:text-white font-sans">${r.drugName || '-'}</td>
                    <td class="py-3 px-3 text-slate-600 dark:text-slate-300 font-mono">${r.avgMonthly ?? '-'}</td>
                    <td class="py-3 px-3 text-slate-600 dark:text-slate-300 font-mono">${r.currentStock ?? '0'}</td>
                    <td class="py-3 px-3 text-slate-500 dark:text-slate-400 font-mono">${r.totalDays || (r.leadDays + r.safetyDays) || '-'} ${t.daysUnit}</td>
                    <td class="py-3 px-3 font-extrabold text-emerald-700 dark:text-emerald-400 text-sm font-mono">${r.recommendedQty ?? '-'}</td>
                </tr>
            `).join('');
        }

        function filterTable() {
            const text = document.getElementById('tableSearch').value.trim();
            renderTable(text);
        }

        function updateKPIs() {
            const countEl = document.getElementById('totalItemsCount');
            const sumEl = document.getElementById('totalQtySum');
            if (countEl) countEl.textContent = records.length;
            const sum = records.reduce((acc, r) => acc + (r.recommendedQty || 0), 0);
            if (sumEl) sumEl.textContent = sum.toLocaleString('en-US');
        }

        function exportToCSV() {
            const t = translations[currentLang];
            if (records.length === 0) {
                alert(t.exportNoData);
                return;
            }
            let csv = t.csvHeader;
            records.forEach(r => {
                csv += `"${r.timestamp || ''}","${r.drugName || ''}","${r.m1 || 0}","${r.m2 || 0}","${r.m3 || 0}","${r.avgMonthly || 0}","${r.leadDays || 0}","${r.safetyDays || 0}","${r.currentStock || 0}","${r.recommendedQty || 0}"\n`;
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

@app.get("/logo.png")
async def get_logo():
    if os.path.exists(LOGO_PATH):
        return FileResponse(LOGO_PATH, media_type="image/png")
    parent_logo = os.path.join(os.path.dirname(BASE_DIR), "logo.png")
    if os.path.exists(parent_logo):
        return FileResponse(parent_logo, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=HTML_TEMPLATE, status_code=200)

@app.post("/api/forecast", response_model=ForecastOutput)
async def calculate_forecast_api(data: ForecastInput):
    drug = (data.drug_name or data.drugName or "").strip()
    
    if re.search(r'[\u0600-\u06FF]', drug):
        raise HTTPException(
            status_code=400,
            detail="Drug name must be entered in English only / يجب كتابة اسم الصنف باللغة الإنجليزية فقط"
        )

    facility = data.facility_name or data.facilityName or "General / عام"
    drug = drug or "Unspecified Drug"
    
    m1 = float(data.m1_consumption or 0.0)
    m2 = float(data.m2_consumption or 0.0)
    m3 = float(data.m3_consumption or 0.0)
    
    # If avg_monthly provided directly without m1, m2, m3
    if data.avg_monthly_consumption and m1 == 0 and m2 == 0 and m3 == 0:
        m1 = m2 = m3 = float(data.avg_monthly_consumption)

    lead_days = float(data.lead_days or data.leadDays or 30.0)
    safety_days = float(data.safety_days or data.safetyDays or 15.0)
    current_stock = float(data.current_stock or data.currentStock or 0.0)

    rec_qty, avg_monthly, daily_demand, total_days = calculate_forecast_logic(
        m1, m2, m3, lead_days, safety_days, current_stock
    )
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return ForecastOutput(
        status="success",
        recommended_qty=rec_qty,
        avg_monthly=avg_monthly,
        daily_demand=daily_demand,
        total_days=total_days,
        timestamp=timestamp_str,
        facility=facility,
        drug=drug
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
