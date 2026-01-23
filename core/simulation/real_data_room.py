import os
import glob
import pdfplumber # <--- THE UPGRADE

class RealDataRoom:
    def __init__(self, folder_path="client_data_room"):
        self.folder_path = folder_path
        self.documents = {}
        self._load_documents()

    def _table_to_markdown(self, table):
        """
        Converts a list of lists (from pdfplumber) into a Markdown table string.
        """
        if not table or len(table) < 2:
            return ""
        
        # Filter out None values
        cleaned_table = [[str(cell) if cell is not None else "" for cell in row] for row in table]
        
        try:
            # Header
            md = "\n\n| " + " | ".join(cleaned_table[0]) + " |\n"
            # Separator
            md += "| " + " | ".join(["---"] * len(cleaned_table[0])) + " |\n"
            # Rows
            for row in cleaned_table[1:]:
                md += "| " + " | ".join(row) + " |\n"
            return md + "\n"
        except Exception:
            return ""

    def _load_documents(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            print(f"⚠️ Created empty folder '{self.folder_path}'. Put client PDFs here!")
            return

        files = glob.glob(os.path.join(self.folder_path, "*.pdf"))
        files.sort()

        print(f"📂 Loading {len(files)} documents using pdfplumber (Table Extraction Enabled)...")

        for i, filepath in enumerate(files):
            filename = os.path.basename(filepath)
            text_content = f"[DOCUMENT START: {filename}]\n"
            
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        # 1. Extract Standard Text
                        text = page.extract_text() or ""
                        
                        # 2. Extract Tables
                        tables = page.extract_tables()
                        table_text = ""
                        if tables:
                            table_text = "\n[DETECTED TABLES]:\n"
                            for table in tables:
                                table_text += self._table_to_markdown(table)
                        
                        # Combine
                        text_content += f"\n--- Page {page_num + 1} ---\n{text}\n{table_text}"
                
                text_content += f"\n[DOCUMENT END: {filename}]"
                self.documents[i] = text_content
                print(f"   ✅ Loaded & Parsed: {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed to load {filename}: {e}")
                self.documents[i] = f"[ERROR READING {filename}]"

    def get_batch_for_shift(self, shift_index: int) -> str:
        if shift_index in self.documents:
            return self.documents[shift_index]
        else:
            return "NO NEW DOCUMENTS. Review the Cumulative Risk Register and finalize the report."
    
    def get_total_docs(self) -> int:
        return len(self.documents)