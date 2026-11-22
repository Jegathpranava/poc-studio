export default function Home() {
  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Operations overview</h1>
          <p className="page-sub">Tuesday depot summary, North region</p>
        </div>
        <button className="btn btn-primary" type="button"><span className="ic ic-plus" /><span>Create shipment</span></button>
      </div>
      <div className="grid cols-4">
        <div className="stat"><span className="stat-label">On-time rate</span><span className="stat-value">94.2%</span><span className="stat-delta up">+1.8 pts vs last week</span></div>
        <div className="stat"><span className="stat-label">Active shipments</span><span className="stat-value">128</span><span className="stat-delta up">+12 since Monday</span></div>
        <div className="stat"><span className="stat-label">Vehicles in service</span><span className="stat-value">41 of 46</span><span className="stat-delta down">5 in maintenance</span></div>
        <div className="stat"><span className="stat-label">Open exceptions</span><span className="stat-value">6</span><span className="stat-delta down">2 need a carrier call</span></div>
      </div>
      <div className="empty">
        <span className="empty-icon"><span className="ic ic-layout-dashboard" /></span>
        <span className="empty-title">Screens appear here</span>
        <span>The Prototype Builder replaces this page with the generated screens.</span>
      </div>
    </>
  );
}
