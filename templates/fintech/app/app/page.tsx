export default function Home() {
  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Treasury overview</h1>
          <p className="page-sub">Business accounts, USD</p>
        </div>
        <button className="btn btn-primary" type="button"><span className="ic ic-plus" /><span>New transfer</span></button>
      </div>
      <div className="grid cols-4">
        <div className="stat"><span className="stat-label">Total balance</span><span className="stat-value">$482,310</span><span className="stat-delta up">+2.1% this month</span></div>
        <div className="stat"><span className="stat-label">Outgoing today</span><span className="stat-value">$38,900</span><span className="stat-delta down">11 scheduled transfers</span></div>
        <div className="stat"><span className="stat-label">Cards active</span><span className="stat-value">18</span><span className="stat-delta up">2 awaiting activation</span></div>
        <div className="stat"><span className="stat-label">Flagged payments</span><span className="stat-value">3</span><span className="stat-delta down">1 over review limit</span></div>
      </div>
      <div className="empty">
        <span className="empty-icon"><span className="ic ic-layout-dashboard" /></span>
        <span className="empty-title">Screens appear here</span>
        <span>The Prototype Builder replaces this page with the generated screens.</span>
      </div>
    </>
  );
}
