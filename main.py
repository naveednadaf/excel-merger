import streamlit as st
import pandas as pd
import io

def main():
    st.title("📊 Excel File Merger")
    st.markdown("Merge two Excel files based on email column and add state information")
    
    # Create two columns for file uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 File A")
        st.markdown("Upload your handpicked/filtered file")
        file_a = st.file_uploader(
            "Choose File A", 
            type=['xlsx', 'xls'], 
            key="file_a",
            help="This should be your Games.xlsx file with handpicked rows"
        )
    
    with col2:
        st.subheader("📁 File B (Full Data)")
        st.markdown("Upload the full data file with email and state columns")
        file_b = st.file_uploader(
            "Choose File B", 
            type=['xlsx', 'xls'], 
            key="file_b",
            help="This should contain email and state columns"
        )
    
    # Configuration options
    st.subheader("⚙️ Configuration")
    
    col3, col4 = st.columns(2)
    with col3:
        merge_column = st.text_input("Reference Column", value="email", help="Column to merge on")
    with col4:
        target_column = st.text_input("Column to Add", value="state", help="Column to add from File B")
    
    # Start Processing Button
    start_processing = st.button("🚀 Start Processing", type="primary", disabled=(file_a is None or file_b is None))
    
    # Process files when both are uploaded and user clicks start
    if start_processing and file_a is not None and file_b is not None:
        try:
            # Load files
            with st.spinner("Loading files..."):
                df_a = pd.read_excel(file_a)
                df_b = pd.read_excel(file_b, usecols=[merge_column, target_column])
            
            # Display file information
            st.subheader("📋 File Information")
            
            col5, col6 = st.columns(2)
            with col5:
                st.info(f"**File A:** {df_a.shape[0]} rows, {df_a.shape[1]} columns")
                with st.expander("Preview File A"):
                    st.dataframe(df_a.head())
            
            with col6:
                st.info(f"**File B:** {df_b.shape[0]} rows, {df_b.shape[1]} columns")
                with st.expander("Preview File B"):
                    st.dataframe(df_b.head())
            
            # Check if merge column exists in both files
            if merge_column not in df_a.columns:
                st.error(f"Column '{merge_column}' not found in File A")
                st.stop()
            
            if merge_column not in df_b.columns:
                st.error(f"Column '{merge_column}' not found in File B")
                st.stop()
                
            if target_column not in df_b.columns:
                st.error(f"Column '{target_column}' not found in File B")
                st.stop()
            
            # Auto-merge process (no additional button needed)
            with st.spinner("Merging files..."):
                # Drop duplicate emails in file_b (keep the original logic)
                df_b_clean = df_b.drop_duplicates(subset=merge_column)
                
                # Merge only the specific column from File B into File A
                merged = df_a.merge(df_b_clean, on=merge_column, how='left')
            
            # Display results
            st.subheader("✅ Merge Results")
            
            # Show statistics
            col7, col8, col9 = st.columns(3)
            with col7:
                st.metric("Total Rows", merged.shape[0])
            with col8:
                matched_count = merged[target_column].notna().sum()
                st.metric("Matched Records", matched_count)
            with col9:
                unmatched_count = merged[target_column].isna().sum()
                st.metric("Unmatched Records", unmatched_count)
            
            # Show preview of merged data
            st.subheader("📊 Merged Data Preview")
            st.dataframe(merged)
            
            # Download functionality
            st.subheader("💾 Download Results")
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                merged.to_excel(writer, index=False, sheet_name='Merged_Data')
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download Games_State.xlsx",
                data=output.getvalue(),
                file_name="Games_State.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Show unmatched records if any
            if unmatched_count > 0:
                with st.expander(f"⚠️ View {unmatched_count} Unmatched Records"):
                    unmatched = merged[merged[target_column].isna()]
                    st.dataframe(unmatched[[merge_column] + [col for col in merged.columns if col != target_column]])
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please make sure your files are valid Excel files and contain the specified columns.")
    
    elif file_a is None or file_b is None:
        st.info("👆 Please upload both files to enable processing")
    
    # Instructions
    with st.expander("ℹ️ How to use this app"):
        st.markdown("""
        1. **Upload File A**: Your handpicked/filtered Excel file 
        2. **Upload File B**: The full data file containing email and state columns
        3. **Configure**: Specify the merge column (default: 'email') and target column (default: 'state')
        4. **Merge**: Click the merge button to process the files
        5. **Download**: Download the merged result as Games_State.xlsx
        
        **Note**: 
        - Duplicate entries in File B will be automatically removed
        - Records from File A that don't have matches in File B will still be included but with empty state values
        - The merge is performed using a 'left join' to preserve all records from File A
        """)

if __name__ == "__main__":
    main()