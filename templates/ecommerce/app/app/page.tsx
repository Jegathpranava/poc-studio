export default function Home() {
  return (
    <>
      <div className="page-head">
        <div>
          <h1 className="page-title">Store overview</h1>
          <p className="page-sub">Today, all sales channels</p>
        </div>
        <button className="btn btn-primary" type="button"><span className="ic ic-plus" /><span>Add product</span></button>
      </div>
      <div className="grid cols-4">
        <div className="stat"><span className="stat-label">Revenue today</span><span className="stat-value">$12,480</span><span className="stat-delta up">+8.4% vs yesterday</span></div>
        <div className="stat"><span className="stat-label">Orders</span><span className="stat-value">214</span><span className="stat-delta up">+19 vs yesterday</span></div>
        <div className="stat"><span className="stat-label">Conversion rate</span><span className="stat-value">3.1%</span><span className="stat-delta down">-0.2 pts vs last week</span></div>
        <div className="stat"><span className="stat-label">Low stock items</span><span className="stat-value">9</span><span className="stat-delta down">3 below reorder point</span></div>
      </div>
      <div className="empty">
        <span className="empty-icon"><span className="ic ic-layout-dashboard" /></span>
        <span className="empty-title">Screens appear here</span>
        <span>The Prototype Builder replaces this page with the generated screens.</span>
      </div>
    </>
  );
}
