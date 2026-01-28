/**
 * useOrderState Hook
 * ==================
 * Gestión centralizada del estado del pedido usando useReducer
 * Incluye persistencia en localStorage para recuperar borradores
 */

import { useReducer, useEffect, useCallback } from 'react';
import { OrderStatus } from '../types';

// =============================================================================
// TYPES
// =============================================================================

export interface ClienteInfo {
  nombre: string;
  email: string;
  telefono: string;
  direccion: {
    calle: string;
    ciudad: string;
    provincia: string;
    cp: string;
  };
}

export interface OrderState {
  step: number;
  productoCodigo: string;
  estiloDiseno: string;
  paginasTotal: number;
  fotos: File[];
  cliente: ClienteInfo;
  metodoPago: 'transferencia' | 'modo';
  comprobante: File | null;
  
  // UI State
  isSubmitting: boolean;
  pedidoId: string | null;
  pedidoEstado: string;
  pedidoProgreso: number;
  
  // Draft tracking
  isDirty: boolean;
}

type OrderAction =
  | { type: 'SET_STEP'; payload: number }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'SET_PRODUCT'; payload: { codigo: string; paginasBase: number } }
  | { type: 'SET_STYLE'; payload: string }
  | { type: 'SET_PAGES'; payload: number }
  | { type: 'ADD_PHOTOS'; payload: File[] }
  | { type: 'REMOVE_PHOTO'; payload: number }
  | { type: 'SET_CLIENTE'; payload: Partial<ClienteInfo> }
  | { type: 'SET_CLIENTE_DIRECCION'; payload: Partial<ClienteInfo['direccion']> }
  | { type: 'SET_METODO_PAGO'; payload: 'transferencia' | 'modo' }
  | { type: 'SET_COMPROBANTE'; payload: File | null }
  | { type: 'SET_SUBMITTING'; payload: boolean }
  | { type: 'SET_PEDIDO_STATUS'; payload: { id?: string; estado?: string; progreso?: number } }
  | { type: 'LOAD_DRAFT'; payload: Partial<OrderState> }
  | { type: 'RESET' };

// =============================================================================
// INITIAL STATE
// =============================================================================

const initialState: OrderState = {
  step: 1,
  productoCodigo: '',
  estiloDiseno: 'clasico',
  paginasTotal: 22,
  fotos: [],
  cliente: {
    nombre: '',
    email: '',
    telefono: '',
    direccion: {
      calle: '',
      ciudad: '',
      provincia: '',
      cp: ''
    }
  },
  metodoPago: 'transferencia',
  comprobante: null,
  
  isSubmitting: false,
  pedidoId: null,
  pedidoEstado: '',
  pedidoProgreso: 0,
  
  isDirty: false
};

// =============================================================================
// REDUCER
// =============================================================================

function orderReducer(state: OrderState, action: OrderAction): OrderState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, step: Math.max(1, Math.min(6, action.payload)) };
    
    case 'NEXT_STEP':
      return { ...state, step: Math.min(state.step + 1, 6) };
    
    case 'PREV_STEP':
      return { ...state, step: Math.max(state.step - 1, 1) };
    
    case 'SET_PRODUCT':
      return { 
        ...state, 
        productoCodigo: action.payload.codigo,
        paginasTotal: action.payload.paginasBase,
        isDirty: true 
      };
    
    case 'SET_STYLE':
      return { ...state, estiloDiseno: action.payload, isDirty: true };
    
    case 'SET_PAGES':
      return { ...state, paginasTotal: action.payload, isDirty: true };
    
    case 'ADD_PHOTOS':
      const newFotos = [...state.fotos, ...action.payload].slice(0, 200);
      return { ...state, fotos: newFotos, isDirty: true };
    
    case 'REMOVE_PHOTO':
      return { 
        ...state, 
        fotos: state.fotos.filter((_, i) => i !== action.payload),
        isDirty: true 
      };
    
    case 'SET_CLIENTE':
      return { 
        ...state, 
        cliente: { ...state.cliente, ...action.payload },
        isDirty: true 
      };
    
    case 'SET_CLIENTE_DIRECCION':
      return { 
        ...state, 
        cliente: { 
          ...state.cliente, 
          direccion: { ...state.cliente.direccion, ...action.payload } 
        },
        isDirty: true 
      };
    
    case 'SET_METODO_PAGO':
      return { ...state, metodoPago: action.payload, isDirty: true };
    
    case 'SET_COMPROBANTE':
      return { ...state, comprobante: action.payload };
    
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.payload };
    
    case 'SET_PEDIDO_STATUS':
      return { 
        ...state, 
        pedidoId: action.payload.id ?? state.pedidoId,
        pedidoEstado: action.payload.estado ?? state.pedidoEstado,
        pedidoProgreso: action.payload.progreso ?? state.pedidoProgreso
      };
    
    case 'LOAD_DRAFT':
      return { ...state, ...action.payload, fotos: [], isDirty: false };
    
    case 'RESET':
      return { ...initialState };
    
    default:
      return state;
  }
}

// =============================================================================
// HOOK
// =============================================================================

const DRAFT_STORAGE_KEY = 'fl_order_draft';

export interface UseOrderStateReturn {
  state: OrderState;
  actions: {
    setStep: (step: number) => void;
    nextStep: () => void;
    prevStep: () => void;
    setProduct: (codigo: string, paginasBase: number) => void;
    setStyle: (id: string) => void;
    setPages: (pages: number) => void;
    addPhotos: (files: File[]) => void;
    removePhoto: (index: number) => void;
    setCliente: (cliente: Partial<ClienteInfo>) => void;
    setClienteDireccion: (direccion: Partial<ClienteInfo['direccion']>) => void;
    setMetodoPago: (metodo: 'transferencia' | 'modo') => void;
    setComprobante: (file: File | null) => void;
    setSubmitting: (value: boolean) => void;
    setPedidoStatus: (status: { id?: string; estado?: string; progreso?: number }) => void;
    reset: () => void;
  };
  
  // Computed
  canProceed: boolean;
  isValid: boolean;
}

export function useOrderState(initialProductCode?: string): UseOrderStateReturn {
  const [state, dispatch] = useReducer(orderReducer, {
    ...initialState,
    productoCodigo: initialProductCode || '',
    step: initialProductCode ? 2 : 1
  });

  // Load draft from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(DRAFT_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        dispatch({ type: 'LOAD_DRAFT', payload: parsed });
      }
    } catch (e) {
      console.error('Error loading draft:', e);
    }
  }, []);

  // Save draft to localStorage when state changes
  useEffect(() => {
    if (state.isDirty) {
      try {
        const toSave = {
          productoCodigo: state.productoCodigo,
          estiloDiseno: state.estiloDiseno,
          paginasTotal: state.paginasTotal,
          cliente: state.cliente,
          metodoPago: state.metodoPago
        };
        localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(toSave));
      } catch (e) {
        console.error('Error saving draft:', e);
      }
    }
  }, [state]);

  // Actions
  const actions = {
    setStep: useCallback((step: number) => 
      dispatch({ type: 'SET_STEP', payload: step }), []),
    
    nextStep: useCallback(() => 
      dispatch({ type: 'NEXT_STEP' }), []),
    
    prevStep: useCallback(() => 
      dispatch({ type: 'PREV_STEP' }), []),
    
    setProduct: useCallback((codigo: string, paginasBase: number) => 
      dispatch({ type: 'SET_PRODUCT', payload: { codigo, paginasBase } }), []),
    
    setStyle: useCallback((id: string) => 
      dispatch({ type: 'SET_STYLE', payload: id }), []),
    
    setPages: useCallback((pages: number) => 
      dispatch({ type: 'SET_PAGES', payload: pages }), []),
    
    addPhotos: useCallback((files: File[]) => 
      dispatch({ type: 'ADD_PHOTOS', payload: files }), []),
    
    removePhoto: useCallback((index: number) => 
      dispatch({ type: 'REMOVE_PHOTO', payload: index }), []),
    
    setCliente: useCallback((cliente: Partial<ClienteInfo>) => 
      dispatch({ type: 'SET_CLIENTE', payload: cliente }), []),
    
    setClienteDireccion: useCallback((direccion: Partial<ClienteInfo['direccion']>) => 
      dispatch({ type: 'SET_CLIENTE_DIRECCION', payload: direccion }), []),
    
    setMetodoPago: useCallback((metodo: 'transferencia' | 'modo') => 
      dispatch({ type: 'SET_METODO_PAGO', payload: metodo }), []),
    
    setComprobante: useCallback((file: File | null) => 
      dispatch({ type: 'SET_COMPROBANTE', payload: file }), []),
    
    setSubmitting: useCallback((value: boolean) => 
      dispatch({ type: 'SET_SUBMITTING', payload: value }), []),
    
    setPedidoStatus: useCallback((status: { id?: string; estado?: string; progreso?: number }) => 
      dispatch({ type: 'SET_PEDIDO_STATUS', payload: status }), []),
    
    reset: useCallback(() => {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
      dispatch({ type: 'RESET' });
    }, [])
  };

  // Computed values
  const canProceed = (() => {
    switch (state.step) {
      case 1: return !!state.productoCodigo;
      case 2: return !!state.estiloDiseno;
      case 3: return state.paginasTotal >= 20 && state.paginasTotal <= 80;
      case 4: return state.fotos.length >= 10;
      case 5: return !!(
        state.cliente.nombre &&
        state.cliente.email &&
        state.cliente.direccion.provincia &&
        state.cliente.direccion.ciudad &&
        state.cliente.direccion.calle &&
        state.cliente.direccion.cp
      );
      case 6: return !!state.metodoPago;
      default: return false;
    }
  })();

  const isValid = !!(
    state.productoCodigo &&
    state.estiloDiseno &&
    state.paginasTotal >= 20 &&
    state.fotos.length >= 10 &&
    state.cliente.nombre &&
    state.cliente.email &&
    state.metodoPago
  );

  return {
    state,
    actions,
    canProceed,
    isValid
  };
}

export default useOrderState;
