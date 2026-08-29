import type { ResearchDocument } from "../api/client";

interface Props {
  documents: ResearchDocument[];
  loading: boolean;
  error: string | null;
  selectedIds: string[];
  searchAll: boolean;
  deletingId: string | null;
  onToggle: (documentId: string) => void;
  onToggleSelectAll: () => void;
  onToggleSearchAll: () => void;
  onDelete: (document: ResearchDocument) => void;
}

export function DocumentList({
  documents,
  loading,
  error,
  selectedIds,
  searchAll,
  deletingId,
  onToggle,
  onToggleSelectAll,
  onToggleSearchAll,
  onDelete,
}: Props) {
  const allSelected =
    documents.length > 0 && selectedIds.length === documents.length;

  return (
    <section className="card">
      <div className="section-heading">
        <h2>Your Documents</h2>
        {documents.length > 0 && (
          <button
            type="button"
            className="secondary-button"
            disabled={searchAll}
            onClick={onToggleSelectAll}
          >
            {allSelected ? "Clear selection" : "Select all"}
          </button>
        )}
      </div>

      <label className="search-all">
        <input
          type="checkbox"
          checked={searchAll}
          onChange={onToggleSearchAll}
        />
        <span>
          <strong>Search all documents</strong>
          <small>
            Use this when you do not know which document contains the answer.
          </small>
        </span>
      </label>

      {loading && <p className="muted">Loading documents...</p>}

      {!loading && error && <p className="error-text">{error}</p>}

      {!loading && !error && documents.length === 0 && (
        <p className="empty-state">
          No documents uploaded yet. Upload a research document to get started.
        </p>
      )}

      {!loading && !error && documents.length > 0 && (
        <ul className="document-list">
          {documents.map((document) => {
            const selected =
              searchAll || selectedIds.includes(document.document_id);

            return (
              <li key={document.document_id}>
                <label className="document-row">
                  <input
                    type="checkbox"
                    checked={selected}
                    disabled={searchAll}
                    onChange={() => onToggle(document.document_id)}
                  />
                  <span title={document.filename}>{document.filename}</span>
                </label>

                <button
                  type="button"
                  className="delete-button"
                  disabled={deletingId === document.document_id}
                  onClick={() => onDelete(document)}
                >
                  {deletingId === document.document_id
                    ? "Deleting..."
                    : "Delete"}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
