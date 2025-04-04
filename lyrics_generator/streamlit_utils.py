import streamlit as st
from contextlib import contextmanager


HORIZONTAL_STYLE = """
<style class="hide-element">
    .element-container:has(.hide-element) {
        display: none;
    }
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
        display: flex;
        flex-direction: row !important;
        flex-wrap: wrap;
        gap: 1.0rem;
        align-items: center;
    }
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
        width: max-content !important;
    }
</style>
"""


@contextmanager
def horizontal():
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="hide-element horizontal-marker"></span>', unsafe_allow_html=True)
        yield
