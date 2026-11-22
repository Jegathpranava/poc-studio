export default function Home() {
  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Clinic overview</h1>
          <p className="page-sub">Thursday, Dr. Ibarra's team</p>
        </div>
        <button className="btn btn-primary" type="button"><span className="ic ic-plus" /><span>Book appointment</span></button>
      </div>
      <div className="grid cols-4">
        <div className="stat"><span className="stat-label">Appointments today</span><span className="stat-value">36</span><span className="stat-delta up">+4 vs typical Thursday</span></div>
        <div className="stat"><span className="stat-label">In waiting room</span><span className="stat-value">5</span><span className="stat-delta down">Longest wait 14 min</span></div>
        <div className="stat"><span className="stat-label">Average wait</span><span className="stat-value">11 min</span><span className="stat-delta up">-3 min vs last week</span></div>
        <div className="stat"><span className="stat-label">Open follow-ups</span><span className="stat-value">14</span><span className="stat-delta down">3 overdue</span></div>
      </div>
      <div className="empty">
        <span className="empty-icon"><span className="ic ic-layout-dashboard" /></span>
        <span className="empty-title">Screens appear here</span>
        <span>The Prototype Builder replaces this page with the generated screens.</span>
      </div>
    </>
  );
}
