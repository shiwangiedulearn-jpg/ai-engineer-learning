import { useEffect, useMemo, useState } from "react";
import {
  askQuestion,
  deleteDocument,
  getDocuments,
  type AskResponse,
  type ResearchDocument,
} from "./api/client";
import { DocumentUpload } from "./components/DocumentUpload";
import { DocumentList } from "./components/DocumentList";
import { QuestionBox } from "./components/QuestionBox";
import { AnswerDisplay } from "./components/AnswerDisplay";

export function App() {
  const [documents, setDocuments] = useState<ResearchDocument[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [searchAll, setSearchAll] = useState(false);

  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [documentError, setDocumentError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<AskResponse | null>(null);

  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function loadDocuments() {
    setLoadingDocuments(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
      setDocumentError(null);
      setSelectedIds((current) =>
        current.filter((id) => data.some((doc) => doc.document_id === id)),
      );
    } catch (error) {
      setDocumentError(getErrorMessage(error));
    } finally {
      setLoadingDocuments(false);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  const documentIdsForSearch = useMemo(() => {
    if (searchAll) {
      return documents.map((doc) => doc.document_id);
    }
    return selectedIds;
  }, [documents, searchAll, selectedIds]);

  function toggleDocument(documentId: string) {
    setSelectedIds((current) =>
      current.includes(documentId)
        ? current.filter((id) => id !== documentId)
        : [...current, documentId],
    );
  }

  function toggleSelectAll() {
    setSelectedIds((current) =>
      current.length === documents.length
        ? []
        : documents.map((doc) => doc.document_id),
    );
  }

  async function handleUploadComplete() {
    setMessage(null);
    await loadDocuments();
  }

  async function handleDelete(document: ResearchDocument) {
    const confirmed = window.confirm(
      `Delete "${document.filename}"? This cannot be undone.`,
    );

    if (!confirmed) return;

    setDeletingId(document.document_id);
    setMessage(null);

    try {
      const response = await deleteDocument(document.document_id);
      setMessage(response.message || `${document.filename} deleted successfully.`);
      setSelectedIds((current) =>
        current.filter((id) => id !== document.document_id),
      );
      await loadDocuments();
    } catch (error) {
      setDocumentError(getErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  }

  async function handleAsk() {
    const trimmedQuestion = question.trim();

    setAskError(null);
    setAnswer(null);

    if (!trimmedQuestion) {
      setAskError("Please enter a question.");
      return;
    }

    if (documentIdsForSearch.length === 0) {
      setAskError(
        documents.length === 0
          ? "Upload a document before asking a question."
          : "Select at least one document or choose Search all documents.",
      );
      return;
    }

    setAsking(true);

    try {
      const response = await askQuestion(
        trimmedQuestion,
        documentIdsForSearch,
      );
      setAnswer(response);
    } catch (error) {
      setAskError(getErrorMessage(error));
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <h1>ResearchRAG</h1>
        <p>Ask questions across your research documents.</p>
      </header>

      <div className="content">
        <DocumentUpload onUploadComplete={handleUploadComplete} />

        {message && <p className="message success">{message}</p>}

        <DocumentList
          documents={documents}
          loading={loadingDocuments}
          error={documentError}
          selectedIds={selectedIds}
          searchAll={searchAll}
          deletingId={deletingId}
          onToggle={toggleDocument}
          onToggleSelectAll={toggleSelectAll}
          onToggleSearchAll={() => setSearchAll((current) => !current)}
          onDelete={handleDelete}
        />

        <QuestionBox
          question={question}
          loading={asking}
          selectedCount={
            searchAll ? documents.length : selectedIds.length
          }
          searchAll={searchAll}
          onChange={setQuestion}
          onAsk={handleAsk}
        />

        {askError && <p className="message error">{askError}</p>}

        <AnswerDisplay answer={answer} loading={asking} />
      </div>
    </main>
  );
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Something went wrong.";
}
