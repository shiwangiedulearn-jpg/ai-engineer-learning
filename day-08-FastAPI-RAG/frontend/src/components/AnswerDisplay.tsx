import type { AskResponse } from "../api/client";

interface Props {
  answer: AskResponse | null;
  loading: boolean;
}

export function AnswerDisplay({ answer, loading }: Props) {
  if (loading) {
    return (
      <section className="card">
        <h2>Answer</h2>
        <p className="muted">
          Searching documents and generating an answer...
        </p>
      </section>
    );
  }

  if (!answer) return null;

  const sources = answer.source ?? answer.sources ?? [];

  return (
    <section className="card">
      <h2>Answer</h2>

      <p className="question-preview">{answer.question}</p>
      <p className="answer-text">{answer.answer}</p>

      {sources.length > 0 && (
        <div className="sources">
          <h3>Sources</h3>
          <ul>
            {sources.map((source) => (
              <li key={source}>{source}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
