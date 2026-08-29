import { useRef, useState } from "react";
import { uploadDocument } from "../api/client";

type UploadStatus = "uploading" | "success" | "error";

interface UploadItem {
  name: string;
  status: UploadStatus;
  message: string;
}

interface Props {
  onUploadComplete: () => void | Promise<void>;
}

const ACCEPTED_TYPES = ".txt,.pdf,.docx";

export function DocumentUpload({ onUploadComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [items, setItems] = useState<UploadItem[]>([]);
  const [uploading, setUploading] = useState(false);

  async function handleUpload() {
    if (files.length === 0 || uploading) return;

    setUploading(true);
    const uploadItems: UploadItem[] = files.map((file) => ({
      name: file.name,
      status: "uploading",
      message: "Uploading...",
    }));
    setItems(uploadItems);

    for (let index = 0; index < files.length; index += 1) {
      try {
        const response = await uploadDocument(files[index]);

        setItems((current) =>
          current.map((item, itemIndex) =>
            itemIndex === index
              ? {
                  ...item,
                  status: "success",
                  message: response.message || "Uploaded successfully.",
                }
              : item,
          ),
        );
      } catch (error) {
        setItems((current) =>
          current.map((item, itemIndex) =>
            itemIndex === index
              ? {
                  ...item,
                  status: "error",
                  message:
                    error instanceof Error
                      ? error.message
                      : "Upload failed.",
                }
              : item,
          ),
        );
      }
    }

    setFiles([]);
    if (inputRef.current) {
      inputRef.current.value = "";
    }

    setUploading(false);
    await onUploadComplete();
  }

  return (
    <section className="card">
      <h2>Upload Documents</h2>
      <p className="muted">Supported formats: TXT, PDF, DOCX</p>

      <div className="upload-row">
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_TYPES}
          onChange={(event) =>
            setFiles(Array.from(event.target.files ?? []))
          }
        />
        <button
          type="button"
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
        >
          {uploading ? "Uploading..." : files.length > 0 ? `Upload ${files.length} file${files.length === 1 ? "" : "s"}` : "Upload"}
        </button>
      </div>

      {items.length > 0 && (
        <ul className="upload-status">
          {items.map((item, index) => (
            <li key={`${item.name}-${index}`}>
              <strong>{item.name}</strong>
              <span
                className={
                  item.status === "error" ? "error-text" : "status-text"
                }
              >
                {item.message}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
