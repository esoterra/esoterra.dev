+++
title = "Confidential Consensus"
date = 2022-12-06
aliases = ["articles/confidential-consensus"]
+++

Currently, the [Confidential Computing] community is focused on use cases with very high security requirements,
like the government and military, where applications must be protected from the Cloud Service Provider or the host machine in general.
These scenarios involve a traditional client/server environment where the server just needs to be a bit more secure.

<figure>
    <img
        src="/cc/figure-0.svg"
        width="450px"
        height="300px"
        alt="Diagram showing a cloud service provider host containing a security critical service guest"
    />
</figure>


Confidential Computing can be used for much more than that though.
As currently envisioned, [Trusted Execution Environments] (TEEs)
provided by Confidential Computing systems offer an exciting trade off built on specialized hardware encryption features.
If you trust the hardware provider, you can run code on data that even the host cannot see or interfere with.

<figure>
    <img
        src="/cc/figure-1.svg"
        width="800px"
        height="250px"
        alt="Diagram showing how a guest in a TEE can be attacked while one not in one can be."
    />
    <figcaption>If you trust the TEE features, you don't have to trust the host</figcaption>
</figure>

This has the potential to enable a new class of federated systems where
the host of a given instance has well-defined limits to the data they can view and the actions they can perform.
If the clients can verify that the instance is running in a TEE and is running open source code they have audited,
they can know what the host can and can't do with their data.
This could be especially valuable in social media & messaging applications where users want to know that their privacy is being protected.

<figure>
    <img
        src="/cc/figure-2.svg"
        width="450px"
        height="450px"
        alt="Diagram showing two users talking to a service instance within a TEE as a way to talk to each other."
    />
    <figcaption>Users can interact through a federated instance without trusting the operator</figcaption>
</figure>

In a fully distributed system, we can achieve <q>Confidential Consensus</q>
where each node runs in a TEE and acts as a replicated state machine processing encrypted events so that some of the system's state remains private.
Such systems will need a way to securely bootstrap so that the initial node(s) are known to be in TEEs
and a way to ensure that any new nodes added to the system are also TEEs.
This approach could offer a more dynamic and redundant version of a federated system where groups of users form networks
representing a given <q>instance</q> or the ability to create a more globally distributed system.

<figure>
    <img
        src="/cc/figure-3.svg"
        width="800px"
        height="570px"
        alt="Diagram showing three TEEs each running a node and users talking to various nodes."
    />
</figure>

To pull this off, Confidential Computing systems will need to be flexible enough that they can run on diverse hardware.
To this end frameworks like [Enarx] that abstract individual hardware security features
and enable cross-platform usage will be crucial.

[Confidential Computing]: https://confidentialcomputing.io/
[Trusted Execution Environments]: https://en.wikipedia.org/wiki/Trusted_execution_environment
[Enarx]: https://enarx.dev/