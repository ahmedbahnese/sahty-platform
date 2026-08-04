import './_group.css';
import { AppLayout } from './_shared/AppLayout';
import {
  Activity, CalendarDays, ChevronRight, Clock3, Download,
  FlaskConical, HeartPulse, Loader2, Pill, ShieldAlert, UserRound
} from 'lucide-react';
import type { CSSProperties, ReactNode } from 'react';
import {
  Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis
} from 'recharts';

// Kept as a named reference so this showcase stays discoverable alongside the application shell.
export const sahtiApplicationShell = AppLayout;

const colors = [
  { group: 'Primary', name: 'Navy 900', hex: '#0A2540', color: '#0A2540', light: false },
  { group: 'Primary', name: 'Navy 700', hex: '#2A4560', color: '#2A4560', light: false },
  { group: 'Primary', name: 'Navy 500', hex: '#4A6580', color: '#4A6580', light: false },
  { group: 'Primary', name: 'Navy 100', hex: '#E4EBF4', color: '#E4EBF4', light: true },
  { group: 'Teal', name: 'Sky 500', hex: '#0EA5E9', color: '#0EA5E9', light: false },
  { group: 'Teal', name: 'Sky 600', hex: '#0284C7', color: '#0284C7', light: false },
  { group: 'Teal', name: 'Sky 300', hex: '#7DD3FC', color: '#7DD3FC', light: true },
  { group: 'Teal', name: 'Sky 50', hex: '#E0F2FE', color: '#E0F2FE', light: true },
  { group: 'Medical', name: 'Emergency', hex: '#EF4444', color: '#EF4444', light: false },
  { group: 'Medical', name: 'Warning', hex: '#F59E0B', color: '#F59E0B', light: false },
  { group: 'Medical', name: 'Success', hex: '#10B981', color: '#10B981', light: false },
  { group: 'Medical', name: 'Info', hex: '#3B82F6', color: '#3B82F6', light: false },
];

const heartRate = [
  { day: 'Sat', rate: 72 }, { day: 'Sun', rate: 76 }, { day: 'Mon', rate: 71 },
  { day: 'Tue', rate: 79 }, { day: 'Wed', rate: 74 }, { day: 'Thu', rate: 68 }, { day: 'Fri', rate: 73 },
];
const appointmentData = [
  { name: 'Completed', value: 42, color: '#10B981' },
  { name: 'Upcoming', value: 18, color: '#0EA5E9' },
  { name: 'Cancelled', value: 6, color: '#E2EBF4' },
];

const cardStyle: CSSProperties = {
  background: 'var(--sahti-surface)', border: '1px solid var(--sahti-border)',
  borderRadius: 16, boxShadow: 'var(--shadow-card)',
};

function Section({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return (
    <section style={{ maxWidth: 1180, margin: '0 auto', padding: '72px 28px 0' }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 20, marginBottom: 28 }}>
        <div>
          <div style={{ color: 'var(--sahti-teal-dark)', fontSize: 11, letterSpacing: 2, fontWeight: 800, textTransform: 'uppercase', marginBottom: 8 }}>{eyebrow}</div>
          <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--sahti-navy)', fontSize: 30, letterSpacing: '-1px', fontWeight: 800 }}>{title}</h2>
        </div>
        <div style={{ height: 1, background: 'var(--sahti-border)', flex: 1, maxWidth: 420, marginBottom: 9 }} />
      </div>
      {children}
    </section>
  );
}

function Status({ label, tone }: { label: string; tone: 'emergency' | 'warning' | 'success' | 'info' | 'pending' | 'scheduled' | 'completed' | 'cancelled' }) {
  const map = {
    emergency: ['#FEF2F2', '#EF4444'], warning: ['#FFFBEB', '#F59E0B'], success: ['#ECFDF5', '#10B981'],
    info: ['#EFF6FF', '#3B82F6'], pending: ['#F8FAFC', '#8BA4BE'], scheduled: ['#E0F2FE', '#0284C7'],
    completed: ['#ECFDF5', '#059669'], cancelled: ['#FEF2F2', '#DC2626'],
  }[tone];
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, borderRadius: 999, padding: '7px 11px', background: map[0], color: map[1], fontSize: 12, fontWeight: 700 }}><i style={{ width: 6, height: 6, borderRadius: 99, background: map[1] }} />{label}</span>;
}

function IconBox({ children, color = 'var(--sahti-teal-pale)' }: { children: ReactNode; color?: string }) {
  return <div style={{ width: 42, height: 42, display: 'grid', placeItems: 'center', borderRadius: 12, color: 'var(--sahti-teal-dark)', background: color }}>{children}</div>;
}

export function DesignSystem() {
  return (
    <>
      <style>{`
        .ds-page { min-height:100dvh; background:var(--sahti-bg); color:var(--sahti-text-primary); font-family:var(--font-body); }
        .ds-page * { box-sizing:border-box; }
        .ds-grid { display:grid; gap:18px; }
        .ds-hover { transition:transform .2s ease, box-shadow .2s ease; }
        .ds-hover:hover { transform:translateY(-3px); box-shadow:var(--shadow-lg)!important; }
        @media (max-width: 700px) { .ds-page section { padding-left:18px!important; padding-right:18px!important; } .ds-hero h1 { font-size:42px!important; } .ds-two { grid-template-columns:1fr!important; } .ds-four { grid-template-columns:1fr 1fr!important; } .ds-type-grid { grid-template-columns:1fr!important; } }
      `}</style>
      <div className="ds-page">
        <header className="bg-mesh-navy ds-hero" style={{ position: 'relative', overflow: 'hidden', padding: '76px 28px 84px', color: 'white' }}>
          <div style={{ position: 'absolute', width: 230, height: 230, border: '1px solid rgba(125,211,252,.18)', borderRadius: '50%', right: '-35px', top: '-78px' }} />
          <div style={{ position: 'absolute', width: 170, height: 170, border: '1px solid rgba(125,211,252,.12)', borderRadius: '50%', right: 7, top: '-48px' }} />
          <div style={{ maxWidth: 1180, margin: '0 auto', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 64 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}><div style={{ width: 40, height: 40, borderRadius: 13, display: 'grid', placeItems: 'center', background: 'linear-gradient(135deg,#0EA5E9,#0284C7)', boxShadow: '0 8px 22px rgba(14,165,233,.3)' }}><HeartPulse size={20} fill="white" /></div><span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 800 }}>صحتك</span></div>
              <span style={{ border: '1px solid rgba(125,211,252,.35)', borderRadius: 999, padding: '7px 12px', color: '#BAE6FD', fontSize: 11, fontWeight: 700 }}>SYSTEM / v2.4.0</span>
            </div>
            <div style={{ maxWidth: 670 }}>
              <div style={{ color: '#7DD3FC', fontSize: 12, fontWeight: 800, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 15 }}>Clarity in care · وضوح في الرعاية</div>
              <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 62, lineHeight: 1.05, letterSpacing: '-2.5px', marginBottom: 20, fontWeight: 800 }}>Sahti Design<br /><span style={{ color: '#7DD3FC' }}>System</span></h1>
              <p style={{ color: 'rgba(255,255,255,.68)', fontSize: 16, lineHeight: 1.8, maxWidth: 540 }}>A calm, confident visual language for the moments that matter most. Built for patients, clinicians, and the teams behind better health.</p>
            </div>
            <div style={{ display: 'flex', gap: 28, marginTop: 56, color: 'rgba(255,255,255,.55)', fontSize: 11, fontWeight: 600 }}><span><b style={{ color: 'white', fontSize: 20, display: 'block' }}>12</b>core colors</span><span><b style={{ color: 'white', fontSize: 20, display: 'block' }}>04</b>status families</span><span><b style={{ color: 'white', fontSize: 20, display: 'block' }}>RTL</b>ready by design</span></div>
          </div>
        </header>

        <Section eyebrow="01 / foundation" title="Color palette">
          <div className="ds-grid ds-four" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>{colors.map(c => <div className="ds-hover" key={c.name} style={{ ...cardStyle, overflow: 'hidden' }}><div style={{ height: 74, background: c.color, borderBottom: c.light ? '1px solid var(--sahti-border)' : 'none' }} /><div style={{ padding: '12px 14px' }}><div style={{ fontSize: 12, fontWeight: 800 }}>{c.name}</div><div style={{ fontSize: 11, color: 'var(--sahti-text-muted)', marginTop: 3 }}>{c.group} · {c.hex}</div></div></div>)}</div>
        </Section>

        <Section eyebrow="02 / type system" title="Typography">
          <div className="ds-grid ds-type-grid" style={{ gridTemplateColumns: '1.35fr .65fr', gap: 18 }}>
            <div style={{ ...cardStyle, padding: 28 }}>
              <div style={{ color: 'var(--sahti-text-muted)', fontSize: 11, fontWeight: 700, marginBottom: 22 }}>PLUS JAKARTA SANS / DISPLAY</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 42, lineHeight: 1.1, fontWeight: 800, letterSpacing: '-1.8px' }}>Care, made clear.</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 25, fontWeight: 700, marginTop: 18 }}>H2 Appointment overview</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 600, marginTop: 13 }}>H3 Your health, at a glance</div>
              <p style={{ color: 'var(--sahti-text-secondary)', fontSize: 14, lineHeight: 1.8, marginTop: 13 }}>The body scale is warm, legible and direct. Every interface decision should reduce uncertainty for the person reading it.</p>
              <div style={{ display: 'flex', gap: 22, marginTop: 22, color: 'var(--sahti-text-muted)', fontSize: 11 }}><span><b style={{ color: 'var(--sahti-navy)' }}>LABEL</b><br />12 / 700</span><span><b style={{ color: 'var(--sahti-navy)' }}>CAPTION</b><br />11 / 500</span></div>
            </div>
            <div style={{ ...cardStyle, padding: 28, direction: 'rtl' }}>
              <div style={{ color: 'var(--sahti-text-muted)', fontSize: 11, fontWeight: 700, direction: 'ltr', marginBottom: 22 }}>CAIRO / ARABIC BODY</div>
              <div style={{ fontFamily: 'var(--font-body)', fontSize: 31, lineHeight: 1.5, fontWeight: 700 }}>صحتك في أمان</div>
              <div style={{ fontFamily: 'var(--font-body)', fontSize: 18, fontWeight: 600, marginTop: 15 }}>مواعيدك الطبية في مكان واحد</div>
              <p style={{ fontSize: 14, lineHeight: 2, color: 'var(--sahti-text-secondary)', marginTop: 12 }}>رعاية واضحة، معلومات موثوقة، وتجربة مصممة لتشعرك بالاطمئنان.</p>
            </div>
          </div>
        </Section>

        <Section eyebrow="03 / semantic states" title="Medical status badges">
          <div style={{ ...cardStyle, padding: 24, display: 'flex', flexWrap: 'wrap', gap: 12 }}>{[['Emergency','emergency'],['Warning','warning'],['Success','success'],['Information','info'],['Pending','pending'],['Scheduled','scheduled'],['Completed','completed'],['Cancelled','cancelled']].map(([label, tone]) => <Status key={label} label={label} tone={tone as never} />)}</div>
        </Section>

        <Section eyebrow="04 / interaction" title="Component library">
          <div style={{ ...cardStyle, padding: 25, display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
            <button style={{ border: 0, borderRadius: 10, padding: '12px 18px', background: 'var(--sahti-teal)', color: 'white', fontWeight: 800, fontFamily: 'inherit', cursor: 'pointer' }}>Book appointment <ChevronRight size={14} style={{ verticalAlign: 'middle', marginLeft: 6 }} /></button>
            <button style={{ border: '1px solid var(--sahti-teal)', borderRadius: 10, padding: '11px 18px', background: 'var(--sahti-teal-pale)', color: 'var(--sahti-teal-dark)', fontWeight: 800, fontFamily: 'inherit', cursor: 'pointer' }}>View records</button>
            <button style={{ border: 0, borderRadius: 10, padding: '12px 18px', background: 'transparent', color: 'var(--sahti-teal-dark)', fontWeight: 800, fontFamily: 'inherit', cursor: 'pointer' }}>Learn more</button>
            <button style={{ border: 0, borderRadius: 10, padding: '12px 18px', background: '#FEF2F2', color: '#DC2626', fontWeight: 800, fontFamily: 'inherit', cursor: 'pointer' }}>Cancel visit</button>
            <button aria-label="Download" style={{ border: '1px solid var(--sahti-border)', borderRadius: 10, width: 43, height: 43, background: 'white', color: 'var(--sahti-text-secondary)', cursor: 'pointer' }}><Download size={16} /></button>
            <button style={{ border: 0, borderRadius: 10, padding: '12px 18px', background: 'var(--sahti-navy)', color: 'white', fontWeight: 800, fontFamily: 'inherit', cursor: 'pointer' }}><Loader2 size={15} className="animate-spin" style={{ verticalAlign: 'middle', marginRight: 7 }} /> Saving…</button>
          </div>
        </Section>

        <Section eyebrow="05 / clinical patterns" title="Medical cards">
          <div className="ds-grid ds-two" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="ds-hover" style={{ ...cardStyle, padding: 22 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div style={{ display: 'flex', gap: 12 }}><IconBox><UserRound size={19} /></IconBox><div><b style={{ fontSize: 15 }}>أحمد الراشدي</b><div style={{ fontSize: 11, color: 'var(--sahti-text-muted)', marginTop: 4 }}>Ahmed Al-Rashidi · PT-20847</div></div></div><Status label="Stable" tone="success" /></div><div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginTop: 22, background: 'var(--sahti-surface-2)', borderRadius: 12, padding: 13 }}><div><small style={{ color: 'var(--sahti-text-muted)' }}>Age</small><b style={{ display: 'block', marginTop: 4 }}>34 yrs</b></div><div><small style={{ color: 'var(--sahti-text-muted)' }}>Blood type</small><b style={{ display: 'block', marginTop: 4 }}>O+</b></div><div><small style={{ color: 'var(--sahti-text-muted)' }}>Last visit</small><b style={{ display: 'block', marginTop: 4 }}>12 May</b></div></div></div>
            <div className="ds-hover" style={{ ...cardStyle, padding: 22 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div style={{ display: 'flex', gap: 12 }}><IconBox><CalendarDays size={19} /></IconBox><div><b style={{ fontSize: 15 }}>Cardiology follow-up</b><div style={{ fontSize: 11, color: 'var(--sahti-text-muted)', marginTop: 4 }}>مع د. سارة الحسن</div></div></div><Status label="Scheduled" tone="scheduled" /></div><div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 22, color: 'var(--sahti-text-secondary)', fontSize: 13 }}><Clock3 size={16} color="var(--sahti-teal)" /> Thu, 16 May · 10:30 AM <span style={{ marginLeft: 'auto', color: 'var(--sahti-teal-dark)', fontWeight: 700 }}>Video visit</span></div></div>
            <div className="ds-hover" style={{ ...cardStyle, padding: 22 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div style={{ display: 'flex', gap: 12 }}><IconBox color="#ECFDF5"><Activity size={19} /></IconBox><div><b style={{ fontSize: 15 }}>Vital signs</b><div style={{ fontSize: 11, color: 'var(--sahti-text-muted)', marginTop: 4 }}>آخر تحديث · منذ 20 دقيقة</div></div></div><Status label="Normal range" tone="success" /></div><div style={{ display: 'flex', gap: 25, marginTop: 22 }}><div><small style={{ color: 'var(--sahti-text-muted)' }}>Heart rate</small><b style={{ display: 'block', fontSize: 22, marginTop: 4 }}>73 <small style={{ fontSize: 11, fontWeight: 500 }}>bpm</small></b></div><div><small style={{ color: 'var(--sahti-text-muted)' }}>Blood pressure</small><b style={{ display: 'block', fontSize: 22, marginTop: 4 }}>118/76</b></div><div><small style={{ color: 'var(--sahti-text-muted)' }}>SpO₂</small><b style={{ display: 'block', fontSize: 22, marginTop: 4 }}>98%</b></div></div></div>
            <div className="ds-hover" style={{ ...cardStyle, padding: 22 }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div style={{ display: 'flex', gap: 12 }}><IconBox color="#EFF6FF"><FlaskConical size={19} /></IconBox><div><b style={{ fontSize: 15 }}>Lipid profile</b><div style={{ fontSize: 11, color: 'var(--sahti-text-muted)', marginTop: 4 }}>تحليل الدهون · 12 May 2024</div></div></div><Status label="Reviewed" tone="info" /></div><div style={{ marginTop: 22, display: 'flex', alignItems: 'baseline', gap: 10 }}><b style={{ fontSize: 27 }}>142</b><span style={{ color: 'var(--sahti-text-secondary)', fontSize: 12 }}>mg/dL total cholesterol</span><span style={{ color: 'var(--sahti-success)', fontSize: 12, fontWeight: 800, marginLeft: 'auto' }}>Within range</span></div></div>
          </div>
        </Section>

        <Section eyebrow="06 / data language" title="Data visualization">
          <div className="ds-grid ds-two" style={{ gridTemplateColumns: '1.45fr .75fr' }}>
            <div style={{ ...cardStyle, padding: 22 }}><div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}><div><b>Heart rate trend</b><div style={{ color: 'var(--sahti-text-muted)', fontSize: 11, marginTop: 4 }}>Resting BPM · Last 7 days</div></div><Status label="Healthy" tone="success" /></div><ResponsiveContainer width="100%" height={205}><AreaChart data={heartRate} margin={{ top: 12, right: 4, left: -25, bottom: 0 }}><defs><linearGradient id="heartFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0EA5E9" stopOpacity={.28} /><stop offset="100%" stopColor="#0EA5E9" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#E2EBF4" vertical={false} /><XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#8BA4BE' }} /><YAxis domain={[60, 85]} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#8BA4BE' }} /><Tooltip contentStyle={{ border: '1px solid #E2EBF4', borderRadius: 10, fontSize: 12 }} /><Area type="monotone" dataKey="rate" stroke="#0EA5E9" strokeWidth={3} fill="url(#heartFill)" /></AreaChart></ResponsiveContainer></div>
            <div style={{ ...cardStyle, padding: 22 }}><b>Appointments</b><div style={{ color: 'var(--sahti-text-muted)', fontSize: 11, marginTop: 4 }}>This quarter · 66 total</div><div style={{ position: 'relative', height: 170 }}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={appointmentData} innerRadius={53} outerRadius={74} dataKey="value" stroke="none" paddingAngle={3}>{appointmentData.map(d => <Cell key={d.name} fill={d.color} />)}</Pie></PieChart></ResponsiveContainer><div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', pointerEvents: 'none' }}><div style={{ textAlign: 'center' }}><b style={{ fontSize: 25 }}>66</b><small style={{ display: 'block', color: 'var(--sahti-text-muted)', fontSize: 10 }}>visits</small></div></div></div><div style={{ display: 'grid', gap: 8 }}>{appointmentData.map(d => <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: 'var(--sahti-text-secondary)' }}><i style={{ width: 7, height: 7, borderRadius: 99, background: d.color }} />{d.name}<b style={{ marginLeft: 'auto', color: 'var(--sahti-navy)' }}>{d.value}</b></div>)}</div></div>
          </div>
        </Section>

        <Section eyebrow="07 / timely care" title="Notification cards">
          <div className="ds-grid ds-two" style={{ gridTemplateColumns: '1fr 1fr', paddingBottom: 90 }}>
            {[
              { title: 'Emergency alert', text: 'Your emergency contact was notified. Help is on the way.', icon: <ShieldAlert size={19} />, bg: '#FEF2F2', color: '#EF4444', label: 'Urgent · now' },
              { title: 'Appointment reminder', text: 'Your video visit with Dr. Sara Hassan starts in 45 minutes.', icon: <CalendarDays size={19} />, bg: '#EFF6FF', color: '#3B82F6', label: 'Today · 9:45 AM' },
              { title: 'Lab result ready', text: 'Your lipid profile has been reviewed and is ready to view.', icon: <FlaskConical size={19} />, bg: '#ECFDF5', color: '#10B981', label: 'New result' },
              { title: 'Medication reminder', text: 'Time to take Atorvastatin 20mg with a glass of water.', icon: <Pill size={19} />, bg: '#FFFBEB', color: '#F59E0B', label: 'Due · 8:00 PM' },
            ].map(n => <div className="ds-hover" key={n.title} style={{ ...cardStyle, padding: 18, display: 'flex', alignItems: 'flex-start', gap: 14, borderLeft: `3px solid ${n.color}` }}><div style={{ width: 40, height: 40, borderRadius: 12, display: 'grid', placeItems: 'center', color: n.color, background: n.bg }}>{n.icon}</div><div style={{ flex: 1 }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}><b style={{ fontSize: 14 }}>{n.title}</b><span style={{ fontSize: 10, color: n.color, fontWeight: 800, whiteSpace: 'nowrap' }}>{n.label}</span></div><p style={{ color: 'var(--sahti-text-secondary)', fontSize: 12, lineHeight: 1.6, marginTop: 7 }}>{n.text}</p></div></div>)}
          </div>
        </Section>
      </div>
    </>
  );
}