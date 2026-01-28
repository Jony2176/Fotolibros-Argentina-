/**
 * StepDelivery Component
 * ======================
 * Paso 5: Datos de entrega del cliente
 */

import React, { useState, useCallback } from 'react';
import { MapPin, User, Mail, Phone, Home, Building, Hash, ChevronDown } from 'lucide-react';
import { PROVINCIAS_MAPPING, CIUDADES_POR_PROVINCIA, CP_POR_CIUDAD } from '../../constants';
import { ClienteInfo } from '../../hooks/useOrderState';
import { PriceBreakdown } from '../../hooks/usePriceCalculation';

interface StepDeliveryProps {
  cliente: ClienteInfo;
  priceBreakdown: PriceBreakdown;
  onClienteChange: (updates: Partial<ClienteInfo>) => void;
  onDireccionChange: (updates: Partial<ClienteInfo['direccion']>) => void;
}

const StepDelivery: React.FC<StepDeliveryProps> = ({
  cliente,
  priceBreakdown,
  onClienteChange,
  onDireccionChange
}) => {
  const [manualCityMode, setManualCityMode] = useState(false);

  const provincias = Object.keys(PROVINCIAS_MAPPING);
  const ciudades = cliente.direccion.provincia 
    ? CIUDADES_POR_PROVINCIA[cliente.direccion.provincia] || []
    : [];

  const handleProvinciaChange = useCallback((provincia: string) => {
    setManualCityMode(false);
    onDireccionChange({ provincia, ciudad: '', cp: '' });
  }, [onDireccionChange]);

  const handleCiudadChange = useCallback((ciudad: string) => {
    if (ciudad === '__other__') {
      setManualCityMode(true);
      onDireccionChange({ ciudad: '' });
    } else {
      const cp = CP_POR_CIUDAD[ciudad] || '';
      onDireccionChange({ ciudad, cp });
    }
  }, [onDireccionChange]);

  // Validation
  const isEmailValid = !cliente.email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cliente.email);
  const isCPValid = !cliente.direccion.cp || /^\d{4}$/.test(cliente.direccion.cp);

  const inputBaseClasses = `
    w-full p-3 md:p-4 bg-white border text-primary font-medium rounded-xl 
    outline-none focus:ring-4 focus:ring-primary/5 focus:border-primary 
    transition-all duration-200 placeholder:text-gray-300 shadow-sm
    min-h-[44px]
  `;

  return (
    <div className="animate-fade-in grid md:grid-cols-3 gap-4 md:gap-6">
      {/* Form Column */}
      <div className="md:col-span-2 space-y-4">
        <h2 className="text-xl md:text-2xl font-display font-bold text-primary">
          Datos de Entrega
        </h2>

        <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 shadow-lg space-y-4">
          {/* Name & Email Row */}
          <div className="grid sm:grid-cols-2 gap-3">
            {/* Name */}
            <div className="space-y-1">
              <label 
                htmlFor="cliente-nombre" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <User className="w-3 h-3" />
                Nombre Completo
              </label>
              <input
                id="cliente-nombre"
                type="text"
                className={`${inputBaseClasses} border-gray-200`}
                placeholder="Juan Perez"
                value={cliente.nombre}
                onChange={(e) => onClienteChange({ nombre: e.target.value })}
                autoComplete="name"
              />
            </div>

            {/* Email */}
            <div className="space-y-1">
              <label 
                htmlFor="cliente-email" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <Mail className="w-3 h-3" />
                Email
              </label>
              <input
                id="cliente-email"
                type="email"
                className={`${inputBaseClasses} ${
                  !isEmailValid ? 'border-red-400 bg-red-50' : 'border-gray-200'
                }`}
                placeholder="tu@email.com"
                value={cliente.email}
                onChange={(e) => onClienteChange({ email: e.target.value })}
                autoComplete="email"
                aria-invalid={!isEmailValid}
                aria-describedby={!isEmailValid ? "email-error" : undefined}
              />
              {!isEmailValid && (
                <span id="email-error" className="text-[9px] text-red-500 ml-1" role="alert">
                  Email invalido
                </span>
              )}
            </div>
          </div>

          {/* Phone (Optional) */}
          <div className="space-y-1">
            <label 
              htmlFor="cliente-telefono" 
              className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
            >
              <Phone className="w-3 h-3" />
              Telefono (opcional)
            </label>
            <input
              id="cliente-telefono"
              type="tel"
              className={`${inputBaseClasses} border-gray-200`}
              placeholder="11 1234-5678"
              value={cliente.telefono}
              onChange={(e) => onClienteChange({ telefono: e.target.value })}
              autoComplete="tel"
            />
          </div>

          {/* Provincia & Ciudad Row */}
          <div className="grid sm:grid-cols-2 gap-3">
            {/* Provincia */}
            <div className="space-y-1">
              <label 
                htmlFor="direccion-provincia" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <MapPin className="w-3 h-3" />
                Provincia
              </label>
              <div className="relative">
                <select
                  id="direccion-provincia"
                  className={`${inputBaseClasses} border-gray-200 appearance-none pr-10`}
                  value={cliente.direccion.provincia}
                  onChange={(e) => handleProvinciaChange(e.target.value)}
                  autoComplete="address-level1"
                >
                  <option value="">Seleccionar...</option>
                  {provincias.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            {/* Ciudad */}
            <div className="space-y-1">
              <label 
                htmlFor="direccion-ciudad" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <Building className="w-3 h-3" />
                Ciudad
              </label>
              {ciudades.length > 0 && !manualCityMode ? (
                <div className="relative">
                  <select
                    id="direccion-ciudad"
                    className={`${inputBaseClasses} border-gray-200 appearance-none pr-10`}
                    value={ciudades.includes(cliente.direccion.ciudad) ? cliente.direccion.ciudad : ''}
                    onChange={(e) => handleCiudadChange(e.target.value)}
                    autoComplete="address-level2"
                  >
                    <option value="">Seleccionar...</option>
                    {ciudades.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                    <option value="__other__">Otra...</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
              ) : (
                <div className="relative">
                  <input
                    id="direccion-ciudad-manual"
                    type="text"
                    className={`${inputBaseClasses} border-gray-200`}
                    placeholder={cliente.direccion.provincia ? "Escribi tu ciudad" : "Primero selecciona provincia"}
                    disabled={!cliente.direccion.provincia}
                    value={cliente.direccion.ciudad}
                    onChange={(e) => onDireccionChange({ ciudad: e.target.value })}
                    autoComplete="address-level2"
                  />
                  {ciudades.length > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        setManualCityMode(false);
                        onDireccionChange({ ciudad: '' });
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-primary font-bold hover:underline min-h-[44px] px-2"
                    >
                      Ver lista
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Address & CP Row */}
          <div className="grid sm:grid-cols-3 gap-3">
            {/* Address */}
            <div className="sm:col-span-2 space-y-1">
              <label 
                htmlFor="direccion-calle" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <Home className="w-3 h-3" />
                Direccion Completa
              </label>
              <input
                id="direccion-calle"
                type="text"
                className={`${inputBaseClasses} border-gray-200`}
                placeholder="Av. Pellegrini 1234, Piso 2, Depto A"
                value={cliente.direccion.calle}
                onChange={(e) => onDireccionChange({ calle: e.target.value })}
                autoComplete="street-address"
              />
            </div>

            {/* CP */}
            <div className="space-y-1">
              <label 
                htmlFor="direccion-cp" 
                className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1 flex items-center gap-1"
              >
                <Hash className="w-3 h-3" />
                Codigo Postal
              </label>
              <input
                id="direccion-cp"
                type="text"
                className={`${inputBaseClasses} ${
                  !isCPValid ? 'border-red-400 bg-red-50' : 'border-gray-200'
                }`}
                placeholder="2000"
                maxLength={4}
                value={cliente.direccion.cp}
                onChange={(e) => onDireccionChange({ 
                  cp: e.target.value.replace(/\D/g, '').slice(0, 4) 
                })}
                autoComplete="postal-code"
                aria-invalid={!isCPValid}
                aria-describedby={!isCPValid ? "cp-error" : undefined}
              />
              {!isCPValid && (
                <span id="cp-error" className="text-[9px] text-red-500 ml-1" role="alert">
                  4 digitos
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Order Summary Column */}
      <div className="md:col-span-1">
        <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 shadow-lg h-fit md:sticky md:top-24 space-y-3">
          <h3 className="font-display font-bold text-primary text-base">Tu Pedido</h3>
          
          <div className="space-y-2 text-sm">
            {/* Product */}
            <div className="flex justify-between">
              <span className="text-gray-400 text-xs">Modelo</span>
              <span className="font-bold text-primary text-xs text-right">
                {priceBreakdown.productName || '-'}
              </span>
            </div>

            {/* Pages */}
            <div className="flex justify-between">
              <span className="text-gray-400 text-xs">Paginas</span>
              <span className="font-bold text-primary text-xs">
                {priceBreakdown.basePagesIncluded + priceBreakdown.extraPages}
              </span>
            </div>

            {/* Shipping */}
            <div className="flex justify-between">
              <span className="text-gray-400 text-xs">Envio</span>
              <span className="font-bold text-primary text-xs">
                {priceBreakdown.shippingCost > 0 
                  ? `$${priceBreakdown.shippingCost.toLocaleString('es-AR')}`
                  : 'Selecciona provincia'
                }
              </span>
            </div>

            {/* Total */}
            <div className="flex justify-between border-t pt-2">
              <span className="text-gray-500 font-bold uppercase text-[10px]">Total</span>
              <span className="text-lg font-display font-bold text-primary">
                {priceBreakdown.formattedSubtotal}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StepDelivery;
