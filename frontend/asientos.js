```javascript
import React from 'react';
import './Asientos.css';

function Asientos({ asientos, asientosVendidos, onSeleccionarAsiento }) {
  return (
    <div className="asientos-container">
      {asientos.map((asiento) => {
        const vendido = asientosVendidos.includes(asiento.id);
        return (
          <button
            key={asiento.id}
            style={{
              backgroundColor: vendido ? 'red' : '', // rojo si vendido
              color: vendido ? 'white' : '',         // texto blanco si vendido
              cursor: vendido ? 'not-allowed' : 'pointer'
            }}
            disabled={vendido}
            onClick={() => {
              if (!vendido) onSeleccionarAsiento(asiento.id);
            }}
          >
            {asiento.numero}
          </button>
        );
      })}
    </div>
  );
}

export default Asientos;
```