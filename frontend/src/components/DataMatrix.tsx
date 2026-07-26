const cells = [
  2, 5, 8, 3, 9, 4, 7, 1, 6, 8, 3, 5,
  7, 1, 4, 9, 2, 6, 5, 8, 3, 7, 9, 2,
  4, 8, 6, 2, 7, 5, 1, 9, 3, 6, 8, 4,
  9, 3, 5, 7, 1, 8, 4, 2, 6, 5, 7, 9,
];

export function DataMatrix() {
  return (
    <div aria-label="Dataset quality specimen" className="matrix-visual">
      <div className="matrix-caption"><span>SPECIMEN 04</span><strong>bounded sample</strong></div>
      <div className="matrix-grid">
        {cells.map((value, index) => (
          <span key={index} style={{ opacity: 0.16 + value / 12 }} />
        ))}
      </div>
      <div className="matrix-axis"><span>coverage</span><span>provenance</span><span>license</span></div>
    </div>
  );
}
