# A mailing list parser
---
This code is useful to recreate the results published in the paper *On the Technical and Social Structure of Community Networks*, In The First IFIP Internet of People Workshop, IoP, 2016 [IEEE link here](http://ieeexplore.ieee.org/document/7497253/) and [pdf here](https://ans.disi.unitn.it/users/maccari/assets/files/bibliography/IoP2016.pdf).

---

This python module will take in input the a mailbox in mbox format, it will parse all the messages and will create a social graph with all the participants to the community as nodes and edges between nodes that exchange at least one reply to the other. It will also compute
the centrality of each node and its individual relevance, plus, the communities using the Louvain method. It will output the results in text and in images if needed.

The simple test_main.py is an example main that takes two input values, one mbox and one list of email aliases. The second is an xml in the form:

    {
        "mail@leonardo.ma (Leonardo Maccari)": [
        [
            1,
            "email->name "
        ],
        [
            "",
            "",
            ""
        ],
        [
            "",
            "",
            ""
        ],
        "\"Leonardo\" <l@leonardo.ma>"
        ]
}

This will translate every "From:" field matching "mail@leonardo.ma (Leonardo Maccari)" to the value "\"Leonardo\" <l@leonardo.ma>". It is useful when multiple From field correspond to the same person and you want to merge them in a single entity. You don't have to create the alis file by hand, check the diffFrom module. If you want to ignore it, just put a file containing "{}".

If you want to test the code, the folder testdata/ contains a small mbox file from a public mailing list of the ninux community network. The email addresses contained in the mbox are modified by mailman in order to prevent spammers to automatically fetch them. The scripts/convert_email.sh script will convert back the addresses to a normal address. Run it before running the parser. **Please do not push the converted mbox archive to any public repository**.

So you can finally run:
    ./mbparse.py ../testdata/wireless-12-2016.txt testdata/aliases.xml and see the results.
 