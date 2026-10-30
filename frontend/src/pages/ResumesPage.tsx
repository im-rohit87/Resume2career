import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Upload, FileText, Trash2, ChevronDown, ChevronUp,
  Plus, X, Save, Loader2, AlertCircle, CheckCircle, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { Resume, ResumeProfile } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';

interface ResumesPageProps {
  onNavigate: (page: string, params?: unknown) => void;
}

function Spinner({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  return <Loader2 className={`animate-spin ${size === 'sm' ? 'w-4 h-4' : 'w-6 h-6'}`} />;
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-500">
        <span>{label}</span>
        <span className="font-semibold text-gray-800">{pct}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function TagInput({
  label, id, tags, onChange,
}: {
  label: string; id: string; tags: string[]; onChange: (t: string[]) => void;
}) {
  const [inputVal, setInputVal] = useState('');
  const addTag = () => {
    const v = inputVal.trim();
    if (v && !tags.includes(v)) onChange([...tags, v]);
    setInputVal('');
  };
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-semibold text-gray-500 mb-1">{label}</label>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {tags.map((t, i) => (
          <span key={i} className="flex items-center gap-1 bg-gray-100 border border-gray-300 text-gray-700 text-xs rounded-lg px-2 py-0.5">
            {t}
            <button type="button" onClick={() => onChange(tags.filter((_, j) => j !== i))} className="text-gray-400 hover:text-rose-400">
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          id={id}
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addTag(); } }}
          className="flex-1 bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-1.5 outline-none"
          placeholder="Type and press Enter"
        />
        <button type="button" onClick={addTag} className="px-3 py-1.5 bg-gray-100 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-300 text-sm">
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export const ResumesPage: React.FC<ResumesPageProps> = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [editProfile, setEditProfile] = useState<ResumeProfile | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');
  const [expandedSection, setExpandedSection] = useState<string | null>('contact');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchResumes = useCallback(async () => {
    try {
      const list = await api.getResumes();
      setResumes(list);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchResumes(); }, [fetchResumes]);

  const validateFile = (file: File): string => {
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
    if (!allowed.includes(file.type) && !file.name.match(/\.(pdf|docx|doc)$/i)) {
      return 'Only PDF or DOCX files are allowed.';
    }
    if (file.size > 5 * 1024 * 1024) return 'File must be under 5 MB.';
    return '';
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) { setUploadError(err); return; }
    setSelectedFile(file);
    setUploadError('');
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) { setUploadError(err); return; }
    setSelectedFile(file);
    setUploadError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadError('');
    try {
      const resume = await api.uploadResume(selectedFile);
      setResumes((prev) => [resume, ...prev]);
      setActiveResume(resume);
      setEditProfile(JSON.parse(JSON.stringify(resume.profile)));
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Upload failed';
      if (msg.toLowerCase().includes('scanned') || msg.toLowerCase().includes('ocr')) {
        setUploadError('This appears to be a scanned PDF. Please upload a text-based PDF or DOCX. Scanned PDFs require OCR which is not currently supported.');
      } else {
        setUploadError(msg);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this resume?')) return;
    try {
      await api.deleteResume(id);
      setResumes((prev) => prev.filter((r) => r.id !== id));
      if (activeResume?.id === id) { setActiveResume(null); setEditProfile(null); }
    } catch (e) { console.error(e); }
  };

  const handleSave = async () => {
    if (!activeResume || !editProfile) return;
    setSaving(true);
    setSaveMsg('');
    try {
      const result = await api.updateResumeProfile(activeResume.id, editProfile);
      const updated = { ...activeResume, profile: result.profile, analysis: result.analysis };
      setActiveResume(updated);
      setResumes((prev) => prev.map((r) => r.id === activeResume.id ? updated : r));
      setSaveMsg('Saved & re-analyzed!');
      setTimeout(() => setSaveMsg(''), 3000);
    } catch (e: unknown) {
      setSaveMsg(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const updateContact = (key: string, val: string) => {
    if (!editProfile) return;
    setEditProfile({ ...editProfile, contact: { ...editProfile.contact, [key]: val } });
  };

  const fmt = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const toggleSection = (s: string) => setExpandedSection((prev) => (prev === s ? null : s));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resumes</h1>
        <p className="text-gray-500 text-sm mt-1">Upload your resume for parsing, analysis, and interview prep.</p>
      </div>

      {/* Upload Zone */}
      <div
        onDrop={handleFileDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          dragOver ? 'border-indigo-500 bg-indigo-500/5' : 'border-gray-300 hover:border-gray-300 bg-white/30'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={handleFileSelect}
        />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        {selectedFile ? (
          <div className="space-y-2">
            <div className="flex items-center justify-center gap-2 text-indigo-400">
              <FileText className="w-5 h-5" />
              <span className="font-semibold">{selectedFile.name}</span>
              <span className="text-gray-400 text-sm">({fmt(selectedFile.size)})</span>
            </div>
            <div className="flex items-center justify-center gap-3 mt-4">
              <button
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); setUploadError(''); }}
                className="px-4 py-2 bg-gray-100 border border-gray-300 text-gray-700 rounded-xl text-sm hover:bg-gray-300"
              >
                Clear
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                disabled={uploading}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold flex items-center gap-2 disabled:opacity-50"
              >
                {uploading ? <Spinner /> : <Upload className="w-4 h-4" />}
                {uploading ? 'Uploading…' : 'Upload & Analyze'}
              </button>
            </div>
          </div>
        ) : (
          <>
            <p className="text-gray-700 font-semibold">Drag & drop your resume here</p>
            <p className="text-gray-400 text-sm mt-1">or <span className="text-indigo-400 underline">click to browse</span></p>
            <p className="text-gray-400 text-xs mt-2">PDF or DOCX · Max 5 MB</p>
          </>
        )}
      </div>

      {uploadError && (
        <div className="flex items-start gap-3 px-4 py-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Resume List */}
      {loading ? (
        <div className="flex items-center justify-center py-12 text-gray-400">
          <Spinner size="md" />
          <span className="ml-3">Loading resumes…</span>
        </div>
      ) : resumes.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
          <p className="font-semibold text-gray-500">No resumes uploaded yet</p>
          <p className="text-sm mt-1">Upload your first resume above to get started.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {resumes.map((r) => (
            <div
              key={r.id}
              className={`flex items-center gap-4 px-4 py-3 bg-white border rounded-xl cursor-pointer transition-all ${
                activeResume?.id === r.id ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => {
                setActiveResume(r);
                setEditProfile(JSON.parse(JSON.stringify(r.profile)));
                setExpandedSection('contact');
              }}
            >
              <FileText className="w-5 h-5 text-indigo-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-gray-800 font-semibold text-sm truncate">{r.filename}</p>
                <p className="text-gray-400 text-xs">{fmt(r.file_size_bytes)} · {new Date(r.created_at).toLocaleDateString()}</p>
              </div>
              {r.analysis && (
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  r.analysis.heuristic_score >= 75 ? 'bg-emerald-500/20 text-emerald-400' :
                  r.analysis.heuristic_score >= 50 ? 'bg-amber-500/20 text-amber-400' :
                  'bg-rose-500/20 text-rose-400'
                }`}>
                  {Math.round(r.analysis.heuristic_score)}/100
                </span>
              )}
              <button
                onClick={(e) => { e.stopPropagation(); handleDelete(r.id); }}
                className="p-1.5 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Active Resume Details */}
      {activeResume && editProfile && (
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Edit Profile */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">Edit Profile</h2>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl disabled:opacity-50"
              >
                {saving ? <Spinner /> : <Save className="w-4 h-4" />}
                {saving ? 'Saving…' : 'Save & Re-analyze'}
              </button>
            </div>
            {saveMsg && (
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${saveMsg.includes('Saved') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                {saveMsg.includes('Saved') ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                {saveMsg}
              </div>
            )}

            {/* Contact */}
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <button
                onClick={() => toggleSection('contact')}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/40"
              >
                <span className="font-semibold text-gray-800 text-sm">Contact Info</span>
                {expandedSection === 'contact' ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>
              {expandedSection === 'contact' && (
                <div className="px-4 pb-4 grid sm:grid-cols-2 gap-3">
                  {(['name', 'email', 'phone', 'location', 'linkedin', 'github'] as const).map((field) => (
                    <div key={field}>
                      <label htmlFor={`contact-${field}`} className="block text-xs text-gray-400 mb-1 capitalize">{field}</label>
                      <input
                        id={`contact-${field}`}
                        type="text"
                        value={(editProfile.contact as Record<string, string | undefined>)[field] || ''}
                        onChange={(e) => updateContact(field, e.target.value)}
                        className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Summary */}
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <button
                onClick={() => toggleSection('summary')}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/40"
              >
                <span className="font-semibold text-gray-800 text-sm">Summary</span>
                {expandedSection === 'summary' ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>
              {expandedSection === 'summary' && (
                <div className="px-4 pb-4">
                  <label htmlFor="summary-text" className="sr-only">Summary</label>
                  <textarea
                    id="summary-text"
                    value={editProfile.summary || ''}
                    onChange={(e) => setEditProfile({ ...editProfile, summary: e.target.value })}
                    rows={4}
                    className="w-full bg-white border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl text-gray-900 text-sm px-3 py-2 outline-none resize-y"
                  />
                </div>
              )}
            </div>

            {/* Skills */}
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <button
                onClick={() => toggleSection('skills')}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/40"
              >
                <span className="font-semibold text-gray-800 text-sm">Skills</span>
                {expandedSection === 'skills' ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>
              {expandedSection === 'skills' && (
                <div className="px-4 pb-4 space-y-3">
                  <TagInput
                    id="skills-technical"
                    label="Technical Skills"
                    tags={editProfile.skills.technical_skills}
                    onChange={(t) => setEditProfile({ ...editProfile, skills: { ...editProfile.skills, technical_skills: t } })}
                  />
                  <TagInput
                    id="skills-frameworks"
                    label="Frameworks & Libraries"
                    tags={editProfile.skills.frameworks_libraries}
                    onChange={(t) => setEditProfile({ ...editProfile, skills: { ...editProfile.skills, frameworks_libraries: t } })}
                  />
                  <TagInput
                    id="skills-tools"
                    label="Tools & Platforms"
                    tags={editProfile.skills.tools_platforms}
                    onChange={(t) => setEditProfile({ ...editProfile, skills: { ...editProfile.skills, tools_platforms: t } })}
                  />
                  <TagInput
                    id="skills-soft"
                    label="Soft Skills"
                    tags={editProfile.skills.soft_skills}
                    onChange={(t) => setEditProfile({ ...editProfile, skills: { ...editProfile.skills, soft_skills: t } })}
                  />
                </div>
              )}
            </div>

            {/* Certifications */}
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <button
                onClick={() => toggleSection('certs')}
                className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-white/40"
              >
                <span className="font-semibold text-gray-800 text-sm">Certifications</span>
                {expandedSection === 'certs' ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>
              {expandedSection === 'certs' && (
                <div className="px-4 pb-4">
                  <TagInput
                    id="certifications"
                    label="Certifications"
                    tags={editProfile.certifications}
                    onChange={(t) => setEditProfile({ ...editProfile, certifications: t })}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Analysis Panel */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Resume Analysis</h2>
            {activeResume.analysis ? (
              <>
                <div className="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col items-center">
                  <ScoreGauge score={activeResume.analysis.heuristic_score} size={160} label="Heuristic Score" />
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-gray-900">Score Breakdown</h3>
                  <ScoreBar label="Contact Completeness" value={activeResume.analysis.score_breakdown.contact_completeness} />
                  <ScoreBar label="Skills Breadth" value={activeResume.analysis.score_breakdown.skills_breadth} />
                  <ScoreBar label="Experience & Projects" value={activeResume.analysis.score_breakdown.experience_and_projects} />
                  <ScoreBar label="Structure & Formatting" value={activeResume.analysis.score_breakdown.structure_and_formatting} />
                  <ScoreBar label="Quantified Metrics" value={activeResume.analysis.score_breakdown.quantified_metrics} />
                </div>

                {activeResume.analysis.strengths.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-2xl p-5">
                    <h3 className="text-sm font-bold text-emerald-400 mb-3">✓ Strengths</h3>
                    <ul className="space-y-1.5">
                      {activeResume.analysis.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-emerald-500 mt-0.5">•</span>{s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {activeResume.analysis.missing_sections.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-2xl p-5">
                    <h3 className="text-sm font-bold text-amber-400 mb-3">⚠ Missing Sections</h3>
                    <div className="flex flex-wrap gap-2">
                      {activeResume.analysis.missing_sections.map((s, i) => (
                        <span key={i} className="text-xs px-2 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-lg">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {activeResume.analysis.actionable_suggestions.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-2xl p-5">
                    <h3 className="text-sm font-bold text-indigo-400 mb-3 flex items-center gap-2">
                      <RefreshCw className="w-4 h-4" /> Suggestions
                    </h3>
                    <ul className="space-y-2">
                      {activeResume.analysis.actionable_suggestions.map((s, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-indigo-400 mt-0.5 font-bold">{i + 1}.</span>{s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <p className="text-xs text-gray-400 italic px-1">{activeResume.analysis.disclaimer}</p>
              </>
            ) : (
              <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-gray-400">
                <p>No analysis available yet.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
