import './_group.css';
import { AppLayout } from './_shared/AppLayout';
import {
  Activity, ArrowUpRight, Bell, CalendarDays, Check, ChevronRight, Clock3, FilePlus2,
  FlaskConical, HeartPulse, MoreHorizontal, Pill, Plus, Radio, RefreshCw, Search,
  Stethoscope, Upload, UserRound, Users, X
} from 'lucide-react';
import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';
import { useState } from 'react';

const visits = [
  { day: 'Sat', visits: 4 }, { day: 'Sun', visits: 6 }, { day: 'Mon', visits: 5 },
  { day: 'Tue', visits: 8 }, { day: 'Wed', visits: 7 }, { day: 'Thu', visits: 3 }, { day: 'Fri', visits: 2 },
];
const diagnoses = [
  { name: 'Cardiac', value: 38, color: '#10B981' },
  { name: 'Hypertension', value: 27, color: '#0EA5E9' },
  { name: 'Diabetes', value: 20, color: '#F59E0B' },
  { name: 'Other', value: 15, color: '#C8D8E8' },
];

const schedule = [
  { time: '08:30', name: 'Mariam Al-Khatib', type: 'Consultation', status: 'Completed', initials: 'MK', tone: '#0EA5E9' },
  { time: '09:15', name: 'Youssef Haddad', type: 'Follow-up', status: 'Completed', initials: 'YH', tone: '#8B5CF6' },
  { time: '10:00', name: 'Layla Mansour', type: 'Consultation', status: 'In Progress', initials: 'LM', tone: '#10B981' },
  { time: '11:30', name: 'Khalid Nasser', type: 'Emergency', status: 'Scheduled', initials: 'KN', tone: '#EF4444' },
  { time: '13:00', name: 'Noor Al-Sayed', type: 'Follow-up', status: 'Scheduled', initials: 'NS', tone: '#F59E0B' },
];
const queue = [
  { name: 'Rania Saad', complaint: 'Palpitations, dizziness', wait: '12 min', color: '#10B981', triage: 'Routine', initials: 'RS' },
  { name: 'Omar Jaber', complaint: 'Chest discomfort', wait: '8 min', color: '#F59E0B', triage: 'Priority', initials: 'OJ' },
  { name: 'Huda Faris', complaint: 'Shortness of breath', wait: '3 min', color: '#EF4444', triage: 'Urgent', initials: 'HF' },
];
const prescriptions = [
  { name: 'Fatima Rahman', meds: 'Bisoprolol 5mg · Atorvastatin 20mg', date: 'Today, 09:42', status: 'Active', tone: 'success' },
  { name: 'Youssef Haddad', meds: 'Aspirin 81mg · Amlodipine 5mg', date: 'Yesterday, 16:18', status: 'Pending Pharmacy', tone: 'warning' },
  { name: 'Mariam Al-Khatib', meds: 'Rosuvastatin 10mg', date: 'Yesterday, 11:05', status: 'Dispensed', tone: 'info' },
];
const results = [
  { name: 'Layla Mansour', test: 'Echocardiogram', date: 'Ordered 18 Jun', status: 'Ready to review', icon: HeartPulse, tone: '#10B981' },
  { name: 'Khalid Nasser', test: 'Troponin I · STAT', date: 'Ordered 18 Jun', status: 'Processing', icon: FlaskConical, tone: '#F59E0B' },
  { name: 'Noor Al-Sayed', test: 'Chest X-Ray', date: 'Ordered 17 Jun', status: 'Ready to review', icon: Radio, tone: '#10B981' },
  { name: 'Rania Saad', test: 'Lipid Panel', date: 'Ordered 17 Jun', status: 'Ready to review', icon: Activity, tone: '#10B981' },
];

const badge = (text: string, tone: 'success' | 'warning' | 'info' | 'danger') => (
  <span className={`badge-${tone === 'danger' ? 'emergency' : tone}`} style={{ fontSize: 10.5, fontWeight: 700, borderRadius: 20, padding: '4px 8px', whiteSpace: 'nowrap' }}>{text}</span>
);

export function DoctorDashboard() {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [called, setCalled] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const trigger = (label: string) => { setActiveAction(label); window.setTimeout(() => setActiveAction(null), 1400); };

  return (
    <AppLayout role="doctor">
      <style>{`
        @keyframes sahtiIn { from { opacity: 0; transform: translateY(8px) } to { opacity: 1; transform: translateY(0) } }
        .doctor-dashboard { animation: sahtiIn .45s ease both; }
        .doctor-card { background: var(--sahti-surface); border: 1px solid var(--sahti-border); border-radius: 14px; box-shadow: var(--shadow-card); }
        .doctor-button { border: 1px solid var(--sahti-border); background: var(--sahti-surface); color: var(--sahti-text-secondary); border-radius: 8px; cursor: pointer; font: 600 11px var(--font-body); transition: transform .15s, border-color .15s, color .15s; }
        .doctor-button:hover { transform: translateY(-1px); border-color: #10B981; color: #047857; }
        .section-title { font: 700 15px var(--font-display); color: var(--sahti-text-primary); }
        .muted { color: var(--sahti-text-muted); font-size: 11px; }
        @media (max-width: 900px) { .doctor-grid { grid-template-columns: 1fr !important; } .stats-grid { grid-template-columns: repeat(2, 1fr) !important; } }
        @media (max-width: 560px) { .stats-grid { grid-template-columns: 1fr !important; } .schedule-actions { display: none !important; } }
      `}</style>
      <div className="doctor-dashboard" style={{ maxWidth: 1500, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, marginBottom: 22, flexWrap: 'wrap' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
              <span style={{ width: 8, height: 8, borderRadius: 99, background: '#10B981', boxShadow: '0 0 0 4px #D1FAE5' }} />
              <span style={{ color: '#047857', fontSize: 11, fontWeight: 700, letterSpacing: .7, textTransform: 'uppercase' }}>Clinical command center</span>
            </div>
            <h1 style={{ font: '800 26px var(--font-display)', letterSpacing: '-.8px', color: 'var(--sahti-text-primary)' }}>Good morning, Dr. Sara</h1>
            <p style={{ color: 'var(--sahti-text-secondary)', fontSize: 13, marginTop: 4 }}>Tuesday, 18 June 2024 <span style={{ color: 'var(--sahti-border-dark)', margin: '0 8px' }}>·</span> Cardiology department</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: '#ECFDF5', border: '1px solid #BBF7D0', color: '#047857', borderRadius: 10, padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 9 }}>
              <CalendarDays size={16} /><div><strong style={{ fontSize: 12 }}>8 appointments today</strong><div style={{ fontSize: 10, color: '#059669' }}>2 pending confirmation</div></div>
            </div>
            <button className="doctor-button" onClick={() => trigger('schedule')} style={{ padding: 11 }}><MoreHorizontal size={17} /></button>
          </div>
        </div>

        <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 18 }}>
          {[
            { label: 'Appointments Today', value: '8', sub: '+2 from yesterday', icon: CalendarDays, color: '#0EA5E9' },
            { label: 'Patients Seen', value: '3', sub: '38% of daily list', icon: Users, color: '#10B981' },
            { label: 'Pending Prescriptions', value: '5', sub: '2 need your review', icon: Pill, color: '#F59E0B' },
            { label: 'Urgent Cases', value: '1', sub: 'Requires attention', icon: Bell, color: '#EF4444' },
          ].map((s) => <div className="doctor-card" key={s.label} style={{ padding: 16, borderTop: `3px solid ${s.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}><span className="muted">{s.label}</span><span style={{ color: s.color, background: `${s.color}14`, borderRadius: 8, padding: 7, display: 'flex' }}><s.icon size={16} /></span></div>
            <div style={{ font: '800 27px var(--font-display)', color: 'var(--sahti-text-primary)', marginTop: 10 }}>{s.value}</div><div style={{ fontSize: 10.5, color: s.color, marginTop: 3 }}>{s.sub}</div>
          </div>)}
        </div>

        <div className="doctor-grid" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.55fr) minmax(300px, .85fr)', gap: 16 }}>
          <div className="doctor-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}><div><div className="section-title">Today's schedule</div><div className="muted" style={{ marginTop: 3 }}>Tuesday, 18 June · Clinic 02</div></div><button className="doctor-button" onClick={() => setShowAll(!showAll)} style={{ padding: '7px 10px' }}>{showAll ? 'Compact view' : 'View calendar'} <ChevronRight size={13} style={{ verticalAlign: 'middle' }} /></button></div>
            <div style={{ borderTop: '1px solid var(--sahti-border)' }}>
              {schedule.map((item, i) => <div key={item.name} style={{ display: 'grid', gridTemplateColumns: '52px 32px minmax(120px, 1fr) auto auto', alignItems: 'center', gap: 12, padding: '12px 0', borderBottom: i < schedule.length - 1 ? '1px solid var(--sahti-border)' : 'none' }}>
                <span style={{ font: '700 12px var(--font-display)', color: item.status === 'In Progress' ? '#047857' : 'var(--sahti-text-secondary)' }}>{item.time}</span>
                <span style={{ width: 31, height: 31, borderRadius: 9, background: `${item.tone}16`, color: item.tone, display: 'grid', placeItems: 'center', font: '700 10px var(--font-display)' }}>{item.initials}</span>
                <div><div style={{ fontWeight: 700, fontSize: 12.5 }}>{item.name}</div><div className="muted" style={{ marginTop: 2 }}>{item.type}</div></div>
                {badge(item.status, item.status === 'Completed' ? 'success' : item.status === 'In Progress' ? 'info' : item.status === 'Emergency' ? 'danger' : 'warning')}
                <div className="schedule-actions" style={{ display: 'flex', gap: 5 }}>{item.status === 'In Progress' ? <button className="doctor-button" onClick={() => trigger('Notes')} style={{ padding: '6px 8px', color: '#047857', borderColor: '#A7F3D0' }}>Notes</button> : <button className="doctor-button" onClick={() => trigger(item.status === 'Completed' ? 'Notes' : 'Start')} style={{ padding: '6px 8px' }}>{item.status === 'Completed' ? 'Notes' : 'Start'}</button>}<button className="doctor-button" onClick={() => trigger('Rescheduled')} style={{ padding: '6px 8px' }}><RefreshCw size={12} /></button></div>
              </div>)}
            </div>
          </div>

          <div className="doctor-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}><div><div className="section-title">Patient queue</div><div className="muted" style={{ marginTop: 3 }}>Live waiting room · 3 patients</div></div><span style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#059669', fontSize: 10, fontWeight: 700 }}><span style={{ width: 6, height: 6, background: '#10B981', borderRadius: 99 }} /> LIVE</span></div>
            {queue.map((p) => <div key={p.name} style={{ padding: '11px 0', borderTop: '1px solid var(--sahti-border)', display: 'grid', gridTemplateColumns: '30px 1fr auto', gap: 10, alignItems: 'center' }}>
              <span style={{ width: 29, height: 29, borderRadius: 8, display: 'grid', placeItems: 'center', background: `${p.color}16`, color: p.color, font: '700 10px var(--font-display)' }}>{p.initials}</span><div><div style={{ fontSize: 12, fontWeight: 700 }}>{p.name}</div><div className="muted">{p.complaint}</div><div style={{ color: p.color, fontSize: 10, fontWeight: 700, marginTop: 3 }}>{p.triage} · waiting {p.wait}</div></div><button className="doctor-button" onClick={() => setCalled(p.name)} style={{ padding: '7px 8px', color: called === p.name ? '#047857' : undefined }}>{called === p.name ? <Check size={13} /> : 'Call next'}</button>
            </div>)}
          </div>
        </div>

        <div className="doctor-grid" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.25fr) minmax(300px, .95fr)', gap: 16, marginTop: 16 }}>
          <div className="doctor-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 13 }}><div><div className="section-title">Recent prescriptions</div><div className="muted" style={{ marginTop: 3 }}>Latest orders from your clinic</div></div><button className="doctor-button" onClick={() => trigger('prescriptions')} style={{ padding: '7px 10px' }}>View all <ArrowUpRight size={12} /></button></div>
            {prescriptions.map((p) => <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '11px 0', borderTop: '1px solid var(--sahti-border)' }}><span style={{ background: '#E0F2FE', color: '#0284C7', borderRadius: 8, padding: 8, display: 'flex' }}><Pill size={15} /></span><div style={{ flex: 1 }}><div style={{ fontSize: 12, fontWeight: 700 }}>{p.name}</div><div className="muted">{p.meds}</div></div><div style={{ textAlign: 'right' }}>{badge(p.status, p.tone as 'success' | 'warning' | 'info')}<div className="muted" style={{ marginTop: 5 }}>{p.date}</div></div></div>)}
          </div>
          <div className="doctor-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 13 }}><div><div className="section-title">Lab & radiology requests</div><div className="muted" style={{ marginTop: 3 }}>4 results waiting for review</div></div><button className="doctor-button" onClick={() => trigger('results')} style={{ padding: '7px 10px' }}>Open inbox <ArrowUpRight size={12} /></button></div>
            {results.map((r) => <div key={r.name} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 0', borderTop: '1px solid var(--sahti-border)' }}><span style={{ color: r.tone, background: `${r.tone}16`, borderRadius: 8, padding: 8, display: 'flex' }}><r.icon size={14} /></span><div style={{ flex: 1 }}><div style={{ fontSize: 11.5, fontWeight: 700 }}>{r.name}</div><div className="muted">{r.test} · {r.date}</div></div><button className="doctor-button" onClick={() => trigger(`Review ${r.name}`)} style={{ padding: '6px 9px' }}>Review</button></div>)}
          </div>
        </div>

        <div className="doctor-grid" style={{ display: 'grid', gridTemplateColumns: '1.35fr 1fr .85fr', gap: 16, marginTop: 16 }}>
          <div className="doctor-card" style={{ padding: 18 }}><div className="section-title">Patient visits</div><div className="muted" style={{ marginTop: 3 }}>This week · 35 visits total</div><div style={{ height: 170, marginTop: 8 }}><ResponsiveContainer width="100%" height="100%"><BarChart data={visits} barSize={18}><CartesianGrid vertical={false} stroke="#E2EBF4" /><XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#8BA4BE' }} /><YAxis hide /><Tooltip cursor={{ fill: '#F0F7FF' }} contentStyle={{ border: '1px solid #E2EBF4', borderRadius: 8, fontSize: 11 }} /><Bar dataKey="visits" fill="#10B981" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div></div>
          <div className="doctor-card" style={{ padding: 18 }}><div className="section-title">Diagnosis mix</div><div className="muted" style={{ marginTop: 3 }}>Across active patients</div><div style={{ height: 130, position: 'relative' }}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={diagnoses} dataKey="value" innerRadius={38} outerRadius={58} paddingAngle={3} stroke="none">{diagnoses.map((d) => <Cell key={d.name} fill={d.color} />)}</Pie></PieChart></ResponsiveContainer><div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', pointerEvents: 'none' }}><strong style={{ font: '800 20px var(--font-display)' }}>100%</strong></div></div><div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>{diagnoses.map(d => <div key={d.name} style={{ fontSize: 10, color: 'var(--sahti-text-secondary)' }}><i style={{ display: 'inline-block', width: 6, height: 6, borderRadius: 99, background: d.color, marginRight: 5 }} />{d.name} {d.value}%</div>)}</div></div>
          <div className="doctor-card bg-mesh-navy" style={{ padding: 18, color: 'white', border: 'none' }}><div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}><div style={{ font: '700 15px var(--font-display)' }}>Quick actions</div><Plus size={18} color="#6EE7B7" /></div><div style={{ color: 'rgba(255,255,255,.6)', fontSize: 11, marginBottom: 14 }}>Keep your clinical flow moving.</div>{[{ label: 'New Prescription', icon: Pill }, { label: 'New Lab Request', icon: FlaskConical }, { label: 'New Radiology Request', icon: Radio }, { label: 'Upload Record', icon: Upload }].map((a) => <button key={a.label} onClick={() => trigger(a.label)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 9, padding: '10px 0', border: 'none', borderTop: '1px solid rgba(255,255,255,.12)', background: 'none', color: 'white', cursor: 'pointer', textAlign: 'left', font: '600 11px var(--font-body)' }}><a.icon size={14} color="#6EE7B7" />{a.label}<ChevronRight size={13} style={{ marginLeft: 'auto', opacity: .55 }} /></button>)}</div>
        </div>
        {activeAction && <div style={{ position: 'fixed', right: 28, bottom: 28, background: '#0A2540', color: 'white', padding: '12px 16px', borderRadius: 10, boxShadow: 'var(--shadow-lg)', fontSize: 12, zIndex: 20 }}>{activeAction} opened <Check size={14} color="#6EE7B7" style={{ verticalAlign: 'middle', marginLeft: 8 }} /></div>}
      </div>
    </AppLayout>
  );
}

export default DoctorDashboard;