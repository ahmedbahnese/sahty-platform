import './_group.css';
import { AppLayout } from './_shared/AppLayout';
import { useMemo, useState } from 'react';
import {
  Activity, AlertTriangle, ArrowUpRight, Check, Clock3,
  Database, FileCheck2, Filter, KeyRound, LockKeyhole, MoreHorizontal,
  Server, ShieldCheck, Sparkles, TrendingUp, UserPlus, Users, Zap
} from 'lucide-react';
import {
  Area, AreaChart, CartesianGrid, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis
} from 'recharts';

const growth = [
  { day: '01', patient: 180, doctor: 26, provider: 14 }, { day: '04', patient: 240, doctor: 31, provider: 19 },
  { day: '07', patient: 220, doctor: 38, provider: 22 }, { day: '10', patient: 310, doctor: 43, provider: 27 },
  { day: '13', patient: 355, doctor: 49, provider: 31 }, { day: '16', patient: 302, doctor: 56, provider: 34 },
  { day: '19', patient: 410, doctor: 62, provider: 38 }, { day: '22', patient: 450, doctor: 68, provider: 45 },
  { day: '25', patient: 498, doctor: 75, provider: 48 }, { day: '28', patient: 535, doctor: 81, provider: 54 },
  { day: '30', patient: 584, doctor: 88, provider: 61 },
];

const approvals = [
  { name: 'Al Noor Specialist Hospital', type: 'Hospital', date: 'Today, 09:42', docs: 8, initials: 'AN', color: '#8B5CF6' },
  { name: 'GulfCare Diagnostics', type: 'Lab', date: 'Yesterday, 16:18', docs: 5, initials: 'GD', color: '#0EA5E9' },
  { name: 'MediPoint Pharmacy Network', type: 'Pharmacy', date: 'May 28, 11:07', docs: 6, initials: 'MP', color: '#10B981' },
];

const activities = [
  ['Login', 'Dr. Hala Mansour signed in', '2 min ago', 'info', KeyRound],
  ['Registration', 'New patient account: Layla Nasser', '8 min ago', 'success', UserPlus],
  ['Prescription', 'Rx issued by Dr. Omar Khalil', '14 min ago', 'purple', FileCheck2],
  ['Emergency', 'Emergency alert acknowledged · ER-4921', '21 min ago', 'danger', AlertTriangle],
  ['Access', 'Admin role granted to Rami Haddad', '35 min ago', 'warning', ShieldCheck],
  ['System', 'AI service model updated to v4.8', '42 min ago', 'info', Sparkles],
  ['Export', 'Audit log exported by Noor Al-Sabah', '1 hr ago', 'muted', Activity],
  ['Security', '2FA policy enabled for providers', '2 hr ago', 'success', LockKeyhole],
] as const;

const users = [
  ['Maha Al-Salem', 'maha.alsalem@sahti.health', 'Patient', 'Active', 'Today, 10:24'],
  ['Dr. Kareem Naji', 'kareem.naji@sahti.health', 'Doctor', 'Active', 'Today, 09:58'],
  ['Rasha Medical Center', 'admin@rasha-med.com', 'Provider', 'Pending', 'Yesterday, 18:21'],
  ['Omar Al-Hadid', 'omar.hadid@sahti.health', 'Patient', 'Active', 'Yesterday, 16:04'],
  ['Dr. Lina Farouq', 'lina.farouq@sahti.health', 'Doctor', 'Suspended', 'May 28, 12:31'],
  ['Atlas Pharmacy', 'ops@atlas-pharmacy.com', 'Provider', 'Active', 'May 27, 08:43'],
];

const services = [
  ['API Server', '99.99%', '42 ms', '#10B981', Server, [38, 35, 36, 34, 39, 35, 32, 34]],
  ['Database', '99.98%', '18 ms', '#10B981', Database, [22, 24, 20, 21, 19, 20, 18, 18]],
  ['File Storage', '99.95%', '67 ms', '#F59E0B', Zap, [49, 52, 48, 59, 54, 60, 66, 67]],
  ['AI Service', '99.91%', '124 ms', '#10B981', Sparkles, [145, 136, 140, 128, 131, 120, 126, 124]],
] as const;

const tone = (kind: string) => ({ info: '#0EA5E9', success: '#10B981', purple: '#8B5CF6', danger: '#EF4444', warning: '#F59E0B', muted: '#8BA4BE' }[kind] || '#0EA5E9');

export function AdminDashboard() {
  const [approved, setApproved] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All users');
  const [toast, setToast] = useState('');
  const [now] = useState(() => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
  const filteredUsers = useMemo(() => users.filter(u => (filter === 'All users' || u[3] === filter) && u.slice(0, 3).join(' ').toLowerCase().includes(query.toLowerCase())), [query, filter]);
  const action = (message: string) => { setToast(message); window.setTimeout(() => setToast(''), 2600); };

  return (
    <AppLayout role="admin">
      <style>{`
        .admin-grid { display:grid; gap:16px; }
        .admin-card { background:var(--sahti-surface); border:1px solid var(--sahti-border); border-radius:14px; box-shadow:var(--shadow-card); }
        .section-title { font-family:var(--font-display); font-size:14px; font-weight:800; color:var(--sahti-text-primary); }
        .eyebrow { font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--sahti-text-muted); font-weight:800; }
        .metric-value { font-family:var(--font-display); font-size:24px; letter-spacing:-.04em; font-weight:800; color:var(--sahti-text-primary); }
        .admin-table { width:100%; border-collapse:collapse; min-width:680px; }
        .admin-table th { text-align:left; font-size:10px; text-transform:uppercase; letter-spacing:.09em; color:var(--sahti-text-muted); padding:11px 14px; border-bottom:1px solid var(--sahti-border); }
        .admin-table td { padding:13px 14px; font-size:12px; color:var(--sahti-text-secondary); border-bottom:1px solid #edf2f7; }
        .admin-table tr:last-child td { border-bottom:0; }
        .admin-table tr:hover td { background:#fbfdff; }
        .pill { border-radius:999px; padding:4px 8px; font-size:10px; font-weight:800; display:inline-flex; align-items:center; gap:4px; }
        @media (min-width: 1100px) { .admin-grid.cols-2 {grid-template-columns:minmax(0,1.48fr) minmax(340px,1fr)} .admin-grid.cols-3 {grid-template-columns:1.15fr .85fr 1fr} }
        @media (max-width: 700px) { .metric-value{font-size:20px} .admin-table{min-width:640px} }
      `}</style>
      {toast && <div style={{ position:'fixed', right:24, bottom:24, zIndex:20, background:'#0A2540', color:'#fff', padding:'12px 16px', borderRadius:10, fontSize:12, boxShadow:'0 8px 24px #0A254044' }}>{toast}</div>}
      <div className="admin-grid" style={{ maxWidth: 1480, margin: '0 auto' }}>
        <header style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-end', gap:16, flexWrap:'wrap' }}>
          <div>
            <div className="eyebrow" style={{ color:'#8B5CF6', marginBottom:7 }}>SAHTI / ADMINISTRATION</div>
            <h1 style={{ fontFamily:'var(--font-display)', fontSize:'clamp(24px,3vw,32px)', letterSpacing:'-.05em', color:'var(--sahti-text-primary)', fontWeight:800 }}>System Control Center</h1>
            <p style={{ color:'var(--sahti-text-secondary)', fontSize:12, marginTop:5 }}>Full platform oversight, security posture, and operational signals.</p>
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <span className="pill" style={{ background:'#ECFDF5', color:'#059669', border:'1px solid #BBF7D0' }}><span style={{ width:6, height:6, borderRadius:99, background:'#10B981' }}/>All Systems Operational</span>
            <span style={{ color:'var(--sahti-text-muted)', fontSize:11, fontFamily:'monospace' }}>LIVE · {now} GST</span>
          </div>
        </header>

        <div className="admin-grid" style={{ gridTemplateColumns:'repeat(5,minmax(150px,1fr))' }}>
          {[['Total Users','12,847','+8.4% vs last month',Users,'#0EA5E9'],['Active Doctors','1,023','+3.1% vs last month',ShieldCheck,'#10B981'],['Appointments Today','3,412','+12.7% vs Tuesday',Activity,'#8B5CF6'],['System Uptime','99.97%','Last 30 days',TrendingUp,'#0EA5E9'],['Pending Approvals','3','Needs attention',Clock3,'#F59E0B']].map(([label,value,sub,Icon,color]) =>
            <div className="admin-card" key={label as string} style={{ padding:16, position:'relative', overflow:'hidden' }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}><span className="eyebrow">{label as string}</span><span style={{ color:color as string, background:`${color}15`, padding:7, borderRadius:9, display:'flex' }}><Icon size={15}/></span></div>
              <div className="metric-value" style={{ marginTop:13 }}>{value as string}</div><div style={{ fontSize:10, color: label === 'Pending Approvals' ? '#D97706' : '#10B981', marginTop:5, fontWeight:700 }}>{sub as string}</div>
            </div>
          )}
        </div>

        <div className="admin-grid cols-2">
          <section className="admin-card" style={{ padding:'18px 18px 10px' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'start' }}><div><div className="section-title">User growth</div><div style={{ fontSize:11, color:'var(--sahti-text-muted)', marginTop:4 }}>New registrations · last 30 days</div></div><button onClick={() => action('Export queued for download')} style={{ border:'1px solid var(--sahti-border)', background:'transparent', color:'var(--sahti-text-secondary)', borderRadius:7, padding:'7px 10px', fontSize:10, cursor:'pointer' }}>Export <ArrowUpRight size={12} style={{ verticalAlign:'middle' }}/></button></div>
            <div style={{ display:'flex', gap:16, margin:'16px 0 2px', fontSize:10, color:'var(--sahti-text-secondary)' }}>{[['Patient','#0EA5E9'],['Doctor','#0A2540'],['Provider','#8B5CF6']].map(x=><span key={x[0]}><i style={{display:'inline-block',width:7,height:7,borderRadius:99,background:x[1],marginRight:5}}/>{x[0]}</span>)}</div>
            <ResponsiveContainer width="100%" height={220}><AreaChart data={growth} margin={{top:10,right:3,left:-25,bottom:0}}><defs><linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0EA5E9" stopOpacity=".2"/><stop offset="100%" stopColor="#0EA5E9" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#edf2f7" vertical={false}/><XAxis dataKey="day" tick={{fontSize:9,fill:'#8BA4BE'}} tickLine={false} axisLine={false}/><YAxis tick={{fontSize:9,fill:'#8BA4BE'}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{border:'1px solid #E2EBF4',borderRadius:8,fontSize:11}}/><Area type="monotone" dataKey="patient" stroke="#0EA5E9" fill="url(#p)" strokeWidth={2} /><Line type="monotone" dataKey="doctor" stroke="#0A2540" strokeWidth={2} dot={false}/><Line type="monotone" dataKey="provider" stroke="#8B5CF6" strokeWidth={2} dot={false}/></AreaChart></ResponsiveContainer>
          </section>

          <section className="admin-card" style={{ padding:18 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'start', marginBottom:14 }}><div><div className="section-title">Pending approvals</div><div style={{ fontSize:11, color:'var(--sahti-text-muted)', marginTop:4 }}>Provider registrations awaiting review</div></div><span className="pill" style={{ background:'#FFF7ED', color:'#D97706' }}>3 queued</span></div>
            <div className="admin-grid" style={{gap:9}}>{approvals.map(a => approved.includes(a.name) ? <div key={a.name} style={{ padding:12, background:'#ECFDF5', borderRadius:10, color:'#059669', fontSize:11, display:'flex', alignItems:'center', gap:8 }}><Check size={14}/> {a.name} approved</div> :
              <div key={a.name} style={{ border:'1px solid #edf2f7', borderRadius:10, padding:11 }}><div style={{display:'flex',gap:10,alignItems:'center'}}><span style={{background:`${a.color}18`,color:a.color,padding:8,borderRadius:8,fontWeight:800,fontSize:11}}>{a.initials}</span><div style={{flex:1}}><div style={{fontSize:12,fontWeight:800,color:'var(--sahti-text-primary)'}}>{a.name}</div><div style={{fontSize:10,color:'var(--sahti-text-muted)',marginTop:3}}>{a.type} · {a.date} · {a.docs} documents</div></div></div><div style={{display:'flex',gap:7,marginTop:10}}><button onClick={()=>setApproved([...approved,a.name])} style={{flex:1,border:0,background:'#0A2540',color:'#fff',borderRadius:6,padding:7,fontSize:10,fontWeight:700,cursor:'pointer'}}>Approve</button><button onClick={()=>action(`${a.name} marked for rejection`)} style={{border:'1px solid #FECACA',background:'#FFF7F7',color:'#DC2626',borderRadius:6,padding:'7px 11px',fontSize:10,fontWeight:700,cursor:'pointer'}}>Reject</button></div></div>)}</div>
          </section>
        </div>

        <div className="admin-grid cols-3">
          <section className="admin-card" style={{ padding:18 }}><div className="section-title">Security overview</div><div className="admin-grid" style={{gridTemplateColumns:'1fr 1fr',gap:9,marginTop:14}}>{[['Failed logins','24','Today','#FEF2F2','#DC2626'],['Active sessions','2,846','Now','#ECFDF5','#059669'],['Rate limit hits','18','Last 24 hours','#FFF7ED','#D97706']].map(x=><div key={x[0]} style={{background:x[3],borderRadius:9,padding:11}}><div style={{fontSize:10,color:'var(--sahti-text-secondary)'}}>{x[0]}</div><div style={{fontSize:20,fontWeight:800,color:x[4],fontFamily:'var(--font-display)',marginTop:5}}>{x[1]}</div><div style={{fontSize:9,color:'var(--sahti-text-muted)',marginTop:3}}>{x[2]}</div></div>)}</div><div style={{marginTop:12,borderTop:'1px solid #edf2f7',paddingTop:13,display:'flex',alignItems:'center',gap:14}}><div style={{width:72,height:72,borderRadius:'50%',background:'conic-gradient(#10B981 0 94%, #E2EBF4 94%)',display:'grid',placeItems:'center'}}><div style={{width:57,height:57,borderRadius:'50%',background:'#fff',display:'grid',placeItems:'center',fontSize:17,fontWeight:800,color:'#059669'}}>94</div></div><div><div style={{fontSize:12,fontWeight:800,color:'var(--sahti-text-primary)'}}>Security score</div><div style={{fontSize:10,color:'var(--sahti-text-muted)',marginTop:3}}>Excellent posture · +2 this week</div></div></div></section>
          <section className="admin-card" style={{ padding:18 }}><div style={{display:'flex',justifyContent:'space-between'}}><div><div className="section-title">Platform health</div><div style={{fontSize:11,color:'var(--sahti-text-muted)',marginTop:4}}>Live service status</div></div><span style={{color:'#10B981',fontSize:10,fontWeight:800}}>● MONITORING</span></div><div className="admin-grid" style={{gap:12,marginTop:16}}>{services.map(([name,up,lat,color,Icon,points])=><div key={name} style={{display:'flex',alignItems:'center',gap:9}}><span style={{color:color as string,background:`${color}15`,padding:7,borderRadius:8,display:'flex'}}><Icon size={14}/></span><div style={{flex:1}}><div style={{display:'flex',justifyContent:'space-between',fontSize:10,fontWeight:700,color:'var(--sahti-text-primary)'}}><span>{name}</span><span style={{color:color as string}}>{up}</span></div><ResponsiveContainer width="100%" height={22}><LineChart data={(points as number[]).map((v,i)=>({i,v}))}><Line type="monotone" dataKey="v" stroke={color as string} strokeWidth={1.7} dot={false}/></LineChart></ResponsiveContainer></div><span style={{fontSize:10,color:'var(--sahti-text-muted)',fontFamily:'monospace'}}>{lat}</span></div>)}</div></section>
          <section className="admin-card" style={{padding:18}}><div className="section-title">System activity</div><div style={{fontSize:11,color:'var(--sahti-text-muted)',marginTop:4,marginBottom:10}}>Real-time audit stream</div><div className="admin-grid" style={{gap:2}}>{activities.map(([type,text,time,kind,Icon])=><div key={text} style={{display:'flex',gap:9,alignItems:'center',padding:'6px 0'}}><span style={{color:tone(kind),background:`${tone(kind)}15`,padding:6,borderRadius:7,display:'flex'}}><Icon size={12}/></span><div style={{flex:1,minWidth:0}}><div style={{fontSize:10,color:'var(--sahti-text-primary)',fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{text}</div><div style={{fontSize:9,color:'var(--sahti-text-muted)',marginTop:2}}>{type} · {time}</div></div></div>)}</div></section>
        </div>

        <section className="admin-card" style={{padding:18, overflow:'hidden'}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,flexWrap:'wrap',marginBottom:13}}><div><div className="section-title">User management</div><div style={{fontSize:11,color:'var(--sahti-text-muted)',marginTop:4}}>12,847 identities across the Sahti platform</div></div><div style={{display:'flex',gap:7}}><div style={{display:'flex',alignItems:'center',gap:6,border:'1px solid var(--sahti-border)',borderRadius:7,padding:'7px 9px'}}><Filter size={12} color="#8BA4BE"/><select value={filter} onChange={e=>setFilter(e.target.value)} style={{border:0,outline:0,fontSize:10,color:'var(--sahti-text-secondary)',background:'transparent'}}><option>All users</option><option>Active</option><option>Pending</option><option>Suspended</option></select></div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search users…" style={{width:150,border:'1px solid var(--sahti-border)',borderRadius:7,padding:'7px 9px',fontSize:10,outline:0}}/></div></div><div style={{overflowX:'auto'}}><table className="admin-table"><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Last login</th><th></th></tr></thead><tbody>{filteredUsers.map(u=><tr key={u[1]}><td><div style={{fontWeight:800,color:'var(--sahti-text-primary)'}}>{u[0]}</div><div style={{fontSize:10,color:'var(--sahti-text-muted)',marginTop:3}}>{u[1]}</div></td><td><span className="pill" style={{background:u[2]==='Doctor'?'#ECFDF5':u[2]==='Provider'?'#EDE9FE':'#E0F2FE',color:u[2]==='Doctor'?'#059669':u[2]==='Provider'?'#7C3AED':'#0284C7'}}>{u[2]}</span></td><td><span className="pill" style={{background:u[3]==='Active'?'#ECFDF5':u[3]==='Pending'?'#FFF7ED':'#FEF2F2',color:u[3]==='Active'?'#059669':u[3]==='Pending'?'#D97706':'#DC2626'}}><span style={{width:5,height:5,borderRadius:99,background:'currentColor'}}/>{u[3]}</span></td><td>{u[4]}</td><td><button onClick={()=>action(`Opening actions for ${u[0]}`)} style={{border:0,background:'transparent',color:'var(--sahti-text-muted)',cursor:'pointer'}}><MoreHorizontal size={16}/></button></td></tr>)}</tbody></table></div></section>
      </div>
    </AppLayout>
  );
}