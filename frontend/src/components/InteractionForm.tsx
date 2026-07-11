import { useEffect, useRef, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { createInteraction, updateInteraction, fetchInteractions } from '../store/interactionsSlice';
import { clearLastInteraction } from '../store/chatSlice';
import type { InteractionCreate } from '../types';
import { SentimentBadge } from './SentimentBadge';
import { IconSpark } from './Icons';

// The logged-in rep. In a real app this comes from auth; hard-coded for the demo.
const REP_NAME = 'Vashu Singh';

const todayLocal = () => {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
};

interface FormState {
  id?: number;
  hcp_name: string;
  specialty: string;
  organization: string;
  product_discussed: string;
  channel: string;
  date: string;
  raw_notes: string;
}

// A fresh empty form — computed each time so the date never goes stale across midnight.
const makeEmpty = (): FormState => ({
  hcp_name: '', specialty: '', organization: '', product_discussed: '',
  channel: 'in-person', date: todayLocal(), raw_notes: '',
});

export function InteractionForm() {
  const dispatch = useAppDispatch();
  const lastInteraction = useAppSelector((s) => s.chat.lastInteraction);
  const { creating, error } = useAppSelector((s) => s.interactions);
  const [form, setForm] = useState<FormState>(makeEmpty);
  // Tracks the last record we synced into the form. Re-sync only when the agent
  // actually creates/changes a record (new id or new updated_at) — otherwise an
  // unrelated chat reply would clobber the rep's in-progress manual edits.
  const syncedKey = useRef<string>('');

  useEffect(() => {
    const it = lastInteraction;
    if (!it) return;
    const key = `${it.id}:${it.updated_at ?? ''}`;
    if (key === syncedKey.current) return;
    syncedKey.current = key;
    setForm({
      id: it.id,
      hcp_name: it.hcp?.name ?? '',
      specialty: it.hcp?.specialty ?? '',
      organization: it.hcp?.organization ?? '',
      product_discussed: it.product_discussed ?? '',
      channel: it.channel ?? 'in-person',
      date: it.date ?? todayLocal(),
      raw_notes: it.raw_notes ?? '',
    });
  }, [lastInteraction]);

  const set = (k: keyof FormState, v: string) => setForm((f) => ({ ...f, [k]: v }));
  const editing = form.id != null;
  const ents = editing ? lastInteraction?.extracted_entities : null;

  const clear = () => {
    syncedKey.current = '';
    setForm(makeEmpty());
    dispatch(clearLastInteraction());
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const done = () => dispatch(fetchInteractions());

    if (editing) {
      // Send only fields the rep actually changed. In particular, resend raw_notes
      // only when edited, so a channel/product tweak doesn't re-run the LLM summary.
      const orig = {
        hcp_name: lastInteraction?.hcp?.name ?? '',
        specialty: lastInteraction?.hcp?.specialty ?? '',
        organization: lastInteraction?.hcp?.organization ?? '',
        product_discussed: lastInteraction?.product_discussed ?? '',
        channel: lastInteraction?.channel ?? '',
        date: lastInteraction?.date ?? '',
        raw_notes: lastInteraction?.raw_notes ?? '',
      };
      const patch: Partial<InteractionCreate> = {};
      if (form.hcp_name.trim() && form.hcp_name !== orig.hcp_name) patch.hcp_name = form.hcp_name;
      if (form.specialty !== orig.specialty) patch.specialty = form.specialty;
      if (form.organization !== orig.organization) patch.organization = form.organization;
      if (form.product_discussed !== orig.product_discussed) patch.product_discussed = form.product_discussed;
      if (form.channel !== orig.channel) patch.channel = form.channel;
      if (form.date && form.date !== orig.date) patch.date = form.date;
      if (form.raw_notes.trim() && form.raw_notes !== orig.raw_notes) patch.raw_notes = form.raw_notes;

      if (Object.keys(patch).length === 0) return; // nothing changed
      dispatch(updateInteraction({ id: form.id!, patch })).then(done);
    } else {
      if (!form.hcp_name.trim() || !form.raw_notes.trim()) return;
      const payload: InteractionCreate = {
        hcp_name: form.hcp_name,
        specialty: form.specialty || undefined,
        organization: form.organization || undefined,
        rep_name: REP_NAME,
        product_discussed: form.product_discussed || undefined,
        channel: form.channel || undefined,
        date: form.date || undefined,
        raw_notes: form.raw_notes,
      };
      dispatch(createInteraction(payload)).then((res) => {
        if (createInteraction.fulfilled.match(res)) clear();
        done();
      });
    }
  };

  return (
    <form onSubmit={submit} className="interaction-form">
      {editing && (
        <div className="ai-flag">
          <IconSpark size={13} /> Filled by AI from chat
          <span className="spacer" />
          <SentimentBadge sentiment={lastInteraction?.sentiment} />
        </div>
      )}

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
          <label>Channel</label>
          <select className="select" value={form.channel} onChange={(e) => set('channel', e.target.value)}>
            <option value="in-person">In-person</option>
            <option value="call">Call</option>
            <option value="virtual">Virtual</option>
          </select>
        </div>
        <div className="field">
          <label>Date</label>
          <input className="input" type="date" value={form.date} onChange={(e) => set('date', e.target.value)} />
        </div>
      </div>

      <div className="field">
        <label>Interaction notes <span className="req">*</span></label>
        <textarea className="textarea"
          placeholder="Describe the visit in the chat on the right — the AI fills this in. You can also type/edit here."
          value={form.raw_notes} onChange={(e) => set('raw_notes', e.target.value)} />
      </div>

      {editing && lastInteraction?.llm_summary && (
        <div className="ai-result">
          <div className="ai-label"><IconSpark size={13} /> AI summary</div>
          <p className="summary">{lastInteraction.llm_summary}</p>
          <div className="tag-row">
            {(ents?.products ?? []).map((p) => <span key={p} className="tag">{p}</span>)}
            {(ents?.key_topics ?? []).map((t) => <span key={t} className="tag">{t}</span>)}
            {ents?.follow_up_date && <span className="tag">follow-up {ents.follow_up_date}</span>}
          </div>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <div className="form-actions">
        <button className="btn btn-primary" disabled={creating}>
          {creating ? 'Saving…' : editing ? 'Save changes' : 'Log interaction'}
        </button>
        {editing && (
          <button type="button" className="btn btn-ghost" onClick={clear}>New</button>
        )}
      </div>
    </form>
  );
}
