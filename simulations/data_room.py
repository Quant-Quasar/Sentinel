class DataRoom:
    def __init__(self):
        self.documents = {
            0: """
            [DOCUMENT: 01_Articles_of_Incorporation.pdf]
            1. Name: Nebula Corp.
            2. Shares: 10,000,000 authorized.
            3. Purpose: To develop AI software.
            4. Board: 3 seats.
            (Standard boilerplate, looks clean.)
            """,
            
            1: """
            [DOCUMENT: 02_CTO_Employment_Agreement.pdf]
            1. Role: Chief Technology Officer.
            2. Salary: $250,000.
            3. IP Assignment: The Company shall own all IP created by Employee during work hours, 
               EXCEPT for the core 'Neural Engine' algorithm, which shall remain the personal property of the Employee 
               and is licensed to the Company on a revocable basis.
            """,
            
            2: """
            [DOCUMENT: 03_Q3_Financials.pdf]
            1. Gross Revenue: $15,000,000.
            2. Net Income: $2,000,000.
            3. EBITDA: $4,500,000.
            
            [DOCUMENT: 03_Financials_Footnotes.pdf]
            * Note 4: 'Gross Revenue' includes $12,000,000 of non-binding Letters of Intent (LOIs) for future services.
            * Note 5: Executive bonuses are excluded from EBITDA calculations.
            """,
            
            3: """
            [DOCUMENT: 04_Vendor_Contracts_Batch_A.pdf]
            1. Server Hosting Agreement: Standard terms.
            2. Office Lease: Expires 2026.
            3. Janitorial Services: $5k/month.
            
            [DOCUMENT: 05_Legacy_Vendor_Contract_Omega.pdf]
            Section 12.4 (Poison Pill): In the event Nebula Corp undergoes a Change of Control (merger or acquisition), 
            Nebula Corp must pay Vendor Omega a one-time liquidation fee of $10,000,000 within 24 hours.
            """,
            
            4: """
            [DOCUMENT: 06_Summary_Review.txt]
            (No new documents. The analyst must review previous findings and finalize the report.)
            """
        }

    def get_batch_for_shift(self, shift_index: int) -> str:
        return self.documents.get(shift_index, "No new documents available. Review existing findings.")