import os
from typing import List, Dict, Any

class KnowledgeBaseLoader:
    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = os.path.abspath(kb_dir)

    def load_chunks(self) -> List[Dict[str, Any]]:
        """
        Parses all .txt files in knowledge_base/ into semantic chunks.
        """
        chunks = []

        if not os.path.exists(self.kb_dir):
            print(f"[RAG Warning] Knowledge directory '{self.kb_dir}' not found.")
            return chunks

        for filename in os.listdir(self.kb_dir):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(self.kb_dir, filename)
            category_name = os.path.splitext(filename)[0].replace("_", " ").title()

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split topics by TOPIC: delimiter
            sections = content.split("TOPIC:")
            for sec in sections:
                cleaned = sec.strip()
                if not cleaned:
                    continue

                lines = cleaned.split("\n")
                topic = lines[0].strip()
                category = category_name
                content_lines = []

                for line in lines[1:]:
                    line_str = line.strip()
                    if line_str.startswith("CATEGORY:"):
                        category = line_str.replace("CATEGORY:", "").strip()
                    elif not line_str.startswith("==="):
                        content_lines.append(line)

                chunk_content = "\n".join(content_lines).strip()
                if chunk_content:
                    chunks.append({
                        "id": f"{category.lower()}-{len(chunks)+1}",
                        "topic": topic,
                        "category": category,
                        "content": chunk_content,
                        "full_text": f"Topic: {topic}\nCategory: {category}\n\n{chunk_content}"
                    })

        return chunks

if __name__ == "__main__":
    loader = KnowledgeBaseLoader()
    items = loader.load_chunks()
    print(f"Loaded {len(items)} knowledge chunk(s).")
