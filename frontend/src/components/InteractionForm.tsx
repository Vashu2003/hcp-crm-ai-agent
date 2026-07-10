import { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { createInteraction, clearLastCreated } from '../store/interactionsSlice';
import type { InteractionCreate } from '../types';
import { SentimentBadge } from './SentimentBadge';

const EMPTY: InteractionCreate = {
  hcp_name: '',
  specialty: '',
  organization: '',
  rep_name: 'Vashu Singh',
  date: new Date().toISOString().slice(0, 10),
  channel: 'in-person',
  product_discussed: '',
  raw_notes: '',
};

export function InteractionForm() {
  const dispatch = useAppDispatch();
  const { creating, lastCreated, error } = useAppSelector((s) => s.interactions);
  const [form, setForm] = useState<InteractionCreate>(EMPTY);

  const set = (k: keyof InteractionCreate, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.hcp_name.trim() || !form.raw_notes.trim()) return;
    dispatch(createInteraction(form)).then((res) => {
      if (createInteraction.fulfilled.match(res)) {
        setForm({ ...EMPTY, date: new Date().toISOString().slice(0, 10) });
      }
    });
  };

  const ents = lastCreated?.extracted_entities;

  return (
    <form onSubmit={submit}>
      <div className="row">
        <div className="field">
          <label>HCP name <span className="req">*</span></label>
          <input className="input" placeholder="Dr. Anita Sharma"
            value={form.hcp_name} onChange={(e) => set('hcp_name', e.target.value)} />
        </div>
        <div className="field">
          <label>Specialty</label>
          <input className="input" placeholder="Cardiology"
            value={form.specialty} onChange={(e) => set('specialty', e.target.value)} />
        </div>
      </div>

      <div className="row">
        <div className="field">
          <label>Organization</label>
          <input className="input" placeholder="Apollo Hospital"
            value={form.organization} onChange={(e) => set('organization', e.target.value)} />
        </div>
        <div className="field">
          <label>Product discussed</label>
          <input className="input" placeholder="Xarelto"
            value={form.product_discussed} onChange={(e) => set('product_discussed', e.target.value)} />
        </div>
      </div>

      <div className="row">
        <div className="field">
          <label>Date</label>
          <input className="input" type="date"
            value={form.date} onChange={(e) => set('date', e.target.value)} />
        </div>
        <div className="field">
          <label>Channel</label>
          <select className="select" value={form.channel} onChange={(e) => set('channel', e.target.value)}>
            <option value="in-person">In-person</option>
            <option value="call">Call</option>
            <option value="virtual">Virtual</option>
          </select>
        </div>
      </div>

      <div className="field">
        <label>Interaction notes <span className="req">*</span></label>
        <textarea className="textarea"
          placeholder="Discussed Xarelto dosing for AF patients. Dr. Sharma keen on new data, wants a lunch-and-learn. Left samples. Follow up next week."
          value={form.raw_notes} onChange={(e) => set('raw_notes', e.target.value)} />
      </div>

      {error && <div className="error-banner">{error}</div>}

      <button className="btn btn-primary btn-block" disabled={creating}>
        {creating ? 'Logging & analyzing…' : '✨ Log interaction'}
      </button>

      {lastCreated && (
        <div className="ai-result">
          <div className="ai-label">✨ AI summary & extraction
            <SentimentBadge sentiment={lastCreated.sentiment} />
          </div>
          <p className="summary">{lastCreated.llm_summary}</p>
          <div className="tag-row">
            {(ents?.products ?? []).map((p) => <span key={p} className="chip">💊 {p}</span>)}
            {(ents?.key_topics ?? []).map((t) => <span key={t} className="chip">{t}</span>)}
            {ents?.follow_up_date && <span className="chip">📅 follow-up {ents.follow_up_date}</span>}
          </div>
          <button type="button" className="btn btn-ghost" style={{ marginTop: 12 }}
            onClick={() => dispatch(clearLastCreated())}>Dismiss</button>
        </div>
      )}
    </form>
  );
}
