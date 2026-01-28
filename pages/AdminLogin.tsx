
import React, { useState } from 'react';

interface AdminLoginProps {
  onSuccess: () => void;
  onBack: () => void;
}

const AdminLogin: React.FC<AdminLoginProps> = ({ onSuccess, onBack }) => {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulation
    if (user === 'admin' && pass === '1234') {
      onSuccess();
    } else {
      setError('Credenciales incorrectas');
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <div className="text-4xl mb-4">📸</div>
          <h1 className="text-2xl font-display font-bold text-primary">Admin Access</h1>
          <p className="text-gray-400 text-sm mt-1">Ingresá tus credenciales para gestionar pedidos</p>
        </div>

        <form onSubmit={handleLogin} className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100 space-y-6">
          {error && <div className="bg-red-50 text-red-600 p-3 rounded-xl text-xs font-bold text-center">{error}</div>}
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Usuario</label>
            <input 
              type="text" 
              className="w-full p-4 bg-gray-50 border-none rounded-2xl outline-none focus:ring-2 ring-primary/10"
              value={user}
              onChange={(e) => setUser(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Contraseña</label>
            <input 
              type="password" 
              className="w-full p-4 bg-gray-50 border-none rounded-2xl outline-none focus:ring-2 ring-primary/10"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
            />
          </div>

          <button className="w-full py-4 bg-primary text-white font-bold rounded-2xl hover:bg-opacity-90 shadow-lg transition-all">
            Ingresar al Panel
          </button>

          <button type="button" onClick={onBack} className="w-full text-xs font-bold text-gray-400 hover:text-primary text-center">
            ← Volver al sitio
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
