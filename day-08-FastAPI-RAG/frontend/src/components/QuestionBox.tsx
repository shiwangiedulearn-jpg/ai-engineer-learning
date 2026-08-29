interface Props {
  question: string;
  loading: boolean;
  selectedCount: number;
  searchAll: boolean;
  onChange: (question: string) => void;
  onAsk: () => void;
}

export function QuestionBox({
  question,
  loading,
  selectedCount,
  searchAll,
  onChange,
  onAsk,
}: Props) {
  const selectionText = searchAll
    ? `Searching across all ${selectedCount} document${selectedCount === 1 ? "" : "s"}.`
    : selectedCount > 0
      ? `${selectedCount} document${selectedCount === 1 ? "" : "s"} selected.`
      : "Select at least one document or choose Search all documents.";

  return (
    <section className="card">
      <h2>Ask a Question</h2>
      <p className="muted">{selectionText}</p>

      <textarea
        value={question}
        rows={5}
        placeholder="Write your research question here..."
        onChange={(event) => onChange(event.target.value)}
      />

      <button
        type="button"
        onClick={onAsk}
        disabled={loading}
      >
        {loading ? "Searching..." : "Ask ResearchRAG"}
      </button>
    </section>
  );
}
