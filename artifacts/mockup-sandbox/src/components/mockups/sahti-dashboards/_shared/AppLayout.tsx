import { useState } from "react";
import {
  Home, Calendar, FileText, Pill, FlaskConical, Radio, Droplets, Building2,
  Users, Settings, Bell, Search, ChevronLeft, ChevronRight, Activity,
  AlertTriangle, Heart, LogOut, User, Shield, Stethoscope, Siren
} from "lucide-react";

export type Role = "patient" | "doctor" | "admin";

interface NavItem {
  icon: React.ReactNode;
  label: string;
  labelAr: string;
  active?: boolean;
  badge?: number | string;
  badgeColor?: string;
}

const NAV_ITEMS: Record<Role, NavItem[]> = {
  patient: [
    { icon: <Home size={18}/>,        label: "Dashboard",       labelAr: "الرئيسية",    active: true },
    { icon: <Calendar size={18}/>,    label: "Appointments",    labelAr: "المواعيد",    badge: 2, badgeColor: "#0EA5E9" },
    { icon: <FileText size={18}/>,    label: "Medical Records", labelAr: "السجل الطبي" },
    { icon: <Pill size={18}/>,        label: "Medications",     labelAr: "الأدوية",     badge: 1, badgeColor: "#F59E0B" },
    { icon: <FlaskConical size={18}/>, label: "Lab Results",    labelAr: "نتائج المخبر" },
    { icon: <Radio size={18}/>,       label: "Radiology",       labelAr: "الأشعة" },
    { icon: <Droplets size={18}/>,    label: "Blood Bank",      labelAr: "بنك الدم" },
    { icon: <Heart size={18}/>,       label: "Family Health",   labelAr: "صحة الأسرة" },
    { icon: <Activity size={18}/>,    label: "Vaccinations",    labelAr: "التطعيمات" },
    { icon: <AlertTriangle size={18}/>, label: "Emergency",     labelAr: "الطوارئ",    badgeColor: "#EF4444" },
  ],
  doctor: [
    { icon: <Home size={18}/>,        label: "Dashboard",       labelAr: "الرئيسية",    active: true },
    { icon: <Users size={18}/>,       label: "My Patients",     labelAr: "مرضاي",       badge: 12 },
    { icon: <Calendar size={18}/>,    label: "Appointments",    labelAr: "المواعيد",    badge: 5, badgeColor: "#0EA5E9" },
    { icon: <FileText size={18}/>,    label: "Prescriptions",   labelAr: "الوصفات الطبية" },
    { icon: <FlaskConical size={18}/>, label: "Lab Requests",   labelAr: "طلبات المخبر" },
    { icon: <Radio size={18}/>,       label: "Radiology",       labelAr: "طلبات الأشعة" },
    { icon: <Activity size={18}/>,    label: "Medical Records", labelAr: "السجلات الطبية" },
    { icon: <Siren size={18}/>,       label: "Emergency",       labelAr: "الطوارئ",    badgeColor: "#EF4444" },
  ],
  admin: [
    { icon: <Home size={18}/>,        label: "Dashboard",       labelAr: "الرئيسية",    active: true },
    { icon: <Users size={18}/>,       label: "Users",           labelAr: "المستخدمون",  badge: 3, badgeColor: "#F59E0B" },
    { icon: <Stethoscope size={18}/>, label: "Doctors",         labelAr: "الأطباء" },
    { icon: <Building2 size={18}/>,   label: "Hospitals",       labelAr: "المستشفيات" },
    { icon: <Activity size={18}/>,    label: "Analytics",       labelAr: "التحليلات" },
    { icon: <FileText size={18}/>,    label: "Audit Logs",      labelAr: "سجلات النظام" },
    { icon: <Shield size={18}/>,      label: "Security",        labelAr: "الأمان",      badge: 1, badgeColor: "#EF4444" },
    { icon: <Settings size={18}/>,    label: "Settings",        labelAr: "الإعدادات" },
  ],
};

const ROLE_META: Record<Role, { label: string; color: string; bg: string; icon: React.ReactNode }> = {
  patient: { label: "Patient Portal",  color: "#0EA5E9", bg: "#E0F2FE", icon: <Heart size={14}/> },
  doctor:  { label: "Doctor Console",  color: "#10B981", bg: "#ECFDF5", icon: <Stethoscope size={14}/> },
  admin:   { label: "Admin Control",   color: "#8B5CF6", bg: "#EDE9FE", icon: <Shield size={14}/> },
};

const USER_META: Record<Role, { name: string; nameAr: string; sub: string }> = {
  patient: { name: "Ahmed Al-Rashidi", nameAr: "أحمد الراشدي", sub: "ID: PT-20847" },
  doctor:  { name: "Dr. Sara Al-Hassan", nameAr: "د. سارة الحسن", sub: "Cardiology · Senior" },
  admin:   { name: "Omar Al-Farouq", nameAr: "عمر الفاروق", sub: "System Administrator" },
};

interface AppLayoutProps {
  role: Role;
  children: React.ReactNode;
}

export function AppLayout({ role, children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const navItems = NAV_ITEMS[role];
  const meta = ROLE_META[role];
  const user = USER_META[role];

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "var(--sahti-bg)", fontFamily: "var(--font-body)" }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: collapsed ? 72 : 260,
        minWidth: collapsed ? 72 : 260,
        background: "var(--sahti-navy)",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.25s ease, min-width 0.25s ease",
        position: "relative",
        overflow: "hidden",
        boxShadow: "4px 0 20px rgba(10,37,64,0.15)",
      }}>
        {/* Mesh overlay */}
        <div style={{
          position: "absolute", inset: 0, pointerEvents: "none",
          background: "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(14,165,233,0.12) 0%, transparent 70%)",
        }}/>

        {/* Logo */}
        <div style={{
          height: 64, display: "flex", alignItems: "center",
          padding: collapsed ? "0 20px" : "0 20px",
          justifyContent: collapsed ? "center" : "space-between",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          position: "relative", zIndex: 1,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 10,
              background: "linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 2px 8px rgba(14,165,233,0.4)",
              flexShrink: 0,
            }}>
              <Heart size={16} color="white" fill="white"/>
            </div>
            {!collapsed && (
              <div>
                <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16, color: "white", letterSpacing: "-0.3px" }}>صحتي</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.45)", letterSpacing: "0.5px", marginTop: -1 }}>SAHTI HEALTH</div>
              </div>
            )}
          </div>
          {!collapsed && (
            <button onClick={() => setCollapsed(true)} style={{
              width: 28, height: 28, borderRadius: 8, border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)", cursor: "pointer", display: "flex",
              alignItems: "center", justifyContent: "center", color: "rgba(255,255,255,0.5)",
              transition: "all 0.15s",
            }}>
              <ChevronLeft size={14}/>
            </button>
          )}
        </div>

        {/* Role badge */}
        {!collapsed && (
          <div style={{ padding: "12px 16px 0", position: "relative", zIndex: 1 }}>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              background: "rgba(255,255,255,0.08)", borderRadius: 20,
              padding: "4px 10px", border: "1px solid rgba(255,255,255,0.1)",
            }}>
              <span style={{ color: meta.color }}>{meta.icon}</span>
              <span style={{ fontSize: 11, fontWeight: 500, color: "rgba(255,255,255,0.7)", letterSpacing: "0.3px" }}>{meta.label}</span>
            </div>
          </div>
        )}

        {/* Nav */}
        <nav style={{ flex: 1, padding: "12px 12px", display: "flex", flexDirection: "column", gap: 2, overflowY: "auto", position: "relative", zIndex: 1 }}>
          {navItems.map((item, i) => (
            <button key={i} style={{
              display: "flex", alignItems: "center", gap: 10,
              padding: collapsed ? "10px 0" : "9px 12px",
              justifyContent: collapsed ? "center" : "flex-start",
              borderRadius: 10, border: "none", cursor: "pointer",
              background: item.active ? "rgba(14,165,233,0.18)" : "transparent",
              color: item.active ? "#7DD3FC" : "rgba(255,255,255,0.55)",
              transition: "all 0.15s",
              position: "relative",
              width: "100%",
            }}>
              {item.active && <div style={{
                position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)",
                width: 3, height: 20, background: "#0EA5E9", borderRadius: "0 2px 2px 0",
              }}/>}
              <span style={{ flexShrink: 0 }}>{item.icon}</span>
              {!collapsed && <span style={{ fontSize: 13.5, fontWeight: item.active ? 600 : 400 }}>{item.label}</span>}
              {!collapsed && item.badge && (
                <span style={{
                  marginLeft: "auto", minWidth: 20, height: 20, borderRadius: 10,
                  background: item.badgeColor || "rgba(255,255,255,0.15)",
                  color: "white", fontSize: 10, fontWeight: 700,
                  display: "flex", alignItems: "center", justifyContent: "center", padding: "0 5px",
                }}>{item.badge}</span>
              )}
            </button>
          ))}
        </nav>

        {/* User + expand toggle */}
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "12px", position: "relative", zIndex: 1 }}>
          {collapsed ? (
            <button onClick={() => setCollapsed(false)} style={{
              width: "100%", height: 40, borderRadius: 10, border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)", cursor: "pointer", display: "flex",
              alignItems: "center", justifyContent: "center", color: "rgba(255,255,255,0.5)",
            }}>
              <ChevronRight size={14}/>
            </button>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{
                width: 36, height: 36, borderRadius: 10,
                background: `linear-gradient(135deg, ${meta.color} 0%, ${meta.color}99 100%)`,
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0, fontSize: 14, fontWeight: 700, color: "white",
              }}>{user.name[0]}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "white", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{user.nameAr}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginTop: 1 }}>{user.sub}</div>
              </div>
              <button style={{ background: "none", border: "none", cursor: "pointer", color: "rgba(255,255,255,0.3)", padding: 4 }}>
                <LogOut size={14}/>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* ── Main ── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Top bar */}
        <header style={{
          height: 64, background: "white", borderBottom: "1px solid var(--sahti-border)",
          display: "flex", alignItems: "center", padding: "0 24px", gap: 16,
          boxShadow: "0 1px 4px rgba(10,37,64,0.04)", flexShrink: 0,
        }}>
          {/* Search */}
          <div style={{
            flex: 1, maxWidth: 440, display: "flex", alignItems: "center", gap: 10,
            background: "var(--sahti-bg)", borderRadius: 10, border: "1.5px solid var(--sahti-border)",
            padding: "0 14px", height: 38,
          }}>
            <Search size={15} color="var(--sahti-text-muted)"/>
            <input placeholder="Search patients, records, appointments…" style={{
              flex: 1, border: "none", background: "none", outline: "none",
              fontSize: 13.5, color: "var(--sahti-text-primary)", fontFamily: "var(--font-body)",
            }}/>
            <kbd style={{
              fontSize: 10, color: "var(--sahti-text-muted)", background: "white",
              border: "1px solid var(--sahti-border)", borderRadius: 4, padding: "1px 5px",
            }}>⌘K</kbd>
          </div>

          <div style={{ flex: 1 }}/>

          {/* Notifications */}
          <button style={{
            width: 38, height: 38, borderRadius: 10, border: "1.5px solid var(--sahti-border)",
            background: "var(--sahti-bg)", cursor: "pointer", display: "flex",
            alignItems: "center", justifyContent: "center", position: "relative",
            color: "var(--sahti-text-secondary)",
          }}>
            <Bell size={16}/>
            <span style={{
              position: "absolute", top: 7, right: 7, width: 8, height: 8,
              background: "#EF4444", borderRadius: "50%", border: "2px solid white",
            }}/>
          </button>

          {/* Role tag */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            background: meta.bg, borderRadius: 20, padding: "5px 12px",
            border: `1px solid ${meta.color}22`,
          }}>
            <span style={{ color: meta.color, display: "flex" }}>{meta.icon}</span>
            <span style={{ fontSize: 12, fontWeight: 600, color: meta.color }}>{meta.label}</span>
          </div>

          {/* Avatar */}
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: `linear-gradient(135deg, ${meta.color} 0%, ${meta.color}99 100%)`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 14, fontWeight: 700, color: "white", cursor: "pointer",
            boxShadow: `0 2px 6px ${meta.color}40`,
          }}>{USER_META[role].name[0]}</div>
        </header>

        {/* Content */}
        <main style={{ flex: 1, overflow: "auto", padding: "24px" }}>
          {children}
        </main>
      </div>
    </div>
  );
}
